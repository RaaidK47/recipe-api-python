""" 
Tests for Recipe API
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from core.models import Tag
from core.models import Ingredient

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

import tempfile
import os
from PIL import Image
from django.contrib.auth import get_user_model
from PIL import Image
from rest_framework.test import APIClient
import tempfile
import os
from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')  #  URL of API

def detail_url(recipe_id):
    """Create and return a recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])
    # ^This is a helper function to create a recipe detail URL
    # ^The args is a list of arguments that will be passed to the function
    # ^The first argument is the recipe_id
    # ^The second argument is the name of the view

def image_upload_url(recipe_id):
    """Create and return an image upload URL"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])
    # ^This is a helper function to create an image upload URL

# Helper Funtion to create a Recipe
def create_recipe(user, **params):
    """Create and return a sample recipe"""
    # params = Dictionary
    
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf',
    }
    # ^default parameters if parameters are not passed

    defaults.update(params)  # Update default with any values that were provided in **params

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


# Helper function to create a user
def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated (public) API requests"""

    def setUp(self):
        self.client = APIClient()  # A test client to use for the Tests in this class (An un-authenticated client)

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        # Recipes can be retreived by users that are Authenticated


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests"""

    # Function Executed before running any tests
    def setUp(self):
        self.client = APIClient()  # A test client to use for the Tests in this class (An Authenticated client)
        self.user = create_user(email="user@example.com", password="test123")  # Create a user to use for the tests (Authenticated)
        self.client.force_authenticate(self.user)  # Force the client to authenticate with the user


    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)  # Creating 2 sample recipes in DB

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')  # We are also going to check the order in which the recipes are returned.
        # Latest Recipes => Highest ID
        # -id >> Return in reverse order (Latest Recipes First)

        serializer = RecipeSerializer(recipes, many=True)  # We expect the result to whatever our Serializer Return
        # How we're going to compare the expected response from the API.
        # many=True  > We want to pass a list of items  (recipes) to our serializer

        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Check Status Code first
        self.assertEqual(res.data, serializer.data)


    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user only"""
        # Making sure that recipes created by a specific user is returned only (User i.e. logged in)
        # i.e. not all the recipes in the Database are returned

        other_user = get_user_model().objects.create_user(
            email='other@example.com',
            password='password123',)

        create_recipe(user=other_user)  # Recipe of New User
        create_recipe(user=self.user)  # Recipe of Current (Authenticated) User (Created by SetUp method)

        res = self.client.get(RECIPES_URL)  # Retreiving Recipe for the user 

        recipes = Recipe.objects.filter(user=self.user)  # Filtering the Recipes created by Current (Authenticated) User 
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)  # Creating a recipe detail URL
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe"""
        # Not using helper function to create Recipe
        # We are actually creating Recipe by passing a Payload
        # To make sure that recipe is correctly and successfully in DB

        # Sample Payload
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }

        res = self.client.post(RECIPES_URL, payload)  # Using APIView to create Recipe (By posting to Recipe Endpoint)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  # Success of Creating new object
        recipe = Recipe.objects.get(id=res.data['id'])  # Getting the recipe object that was created (by id that is returned from Response)

        for k, v in payload.items():
            # k = key = name/title
            # v = value = assigned to that title
            # getattr(recipe, k) >> Get the value of the key (name/title) from the recipe object

            self.assertEqual(getattr(recipe, k), v)
            # ^ Comparing Returned object `Values` with `Values of Payload` 

        self.assertEqual(recipe.user, self.user)  # Making sure that User Assigned to API is same as User we're authenticated with.


    ## v Wrinting Optional Tests (To Increase Software Robustness)

    def test_partial_update(self):
        """Test Partial Update of a Recipe"""

        original_link = 'https://example.com/recipe.pdf'
        
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link=original_link,
        )

        payload = {'title': 'New recipe title'}

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        recipe.refresh_from_db()  # To refresh the recipe (i.e. Pull from Database)

        self.assertEqual(recipe.title, payload['title'])  # Only title has to be changed
        self.assertEqual(recipe.link, original_link)  # Testing that original link is not updated during PATCH (Partial Update) operation
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test Full Update of a Recipe"""

        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link='https://example.com/recipe.pdf',
            description='Sample recipe description',
        )

        payload = {
            'title': 'New recipe title',
            'link': 'https://example.com/new-recipe.pdf',
            'description': 'New recipe description',
            'time_minutes': 10,
            'price': Decimal('2.50'),
        }

        url = detail_url(recipe.id)
        res = self.client.put(url, payload)  # PUT == Full Update (Every Single Field has to be provided)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()  # To refresh the recipe (i.e. Pull from Database)

        for k, v in payload.items():
            # k = key = name/title
            # v = value = assigned to that title
            # getattr(recipe, k) >> Get the value of the key (name/title) from the recipe object"""

            self.assertEqual(getattr(recipe, k), v)
        
        self.assertEqual(recipe.user, self.user)


    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error"""

        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=self.user)  # Recipe Created by default user (as defined in SetUp())

        payload = {'user': new_user.id}  # Trying to change the user of the recipe to a new user (new_user)
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.user)  # Making sure that the recipe user is not changed


    def test_delete_recipe(self):
        """Test deleting a recipe successful"""

        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)  # 204 = No Content (Delete Successful and No Content to Return)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())  # Making sure that the recipe is deleted"""
        # ^ Checking that an Object Exist in DB or not


    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete another users recipe gives error"""

        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)  # The Client Belongs to Defualt User (Authenticated User)
        # ^Trying to delete another user's recipe  

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())  # Making sure that the recipe is not deleted"""
        # ^ Checking that an Object Exist in DB or not


    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags"""

        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],
        }

        res = self.client.post(RECIPES_URL, payload, format='json')  # format='json' > required when posting nested object

        self.assertEqual(res.status_code, status.HTTP_201_CREATED) 

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)  # Checking that the recipe is created
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)  # Checking that 2x tags are created

        # Checking that tags with correct name and user exist
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    # To assign an already existent tag in database to new recipe
    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tag"""

        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}],
        }

        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)  # We expect that only Two Tags are Created (instead of 3)
        self.assertIn(tag_indian, recipe.tags.all())  # Checking that the tag_indian is assigned to the recipe (instead of creating a new tag)  

        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)


    def test_create_tag_on_update(self):
        """Test creating tag when updating a recipe"""
        # When Updating a Recipe with a new Tag and the Tag does not exist in the Database, we create the Tag

        recipe = create_recipe(user=self.user)

        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        # recipe.refresh_from_db() is not required whne using ManytoMany field
        # Because it is executing a new query under the hood

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Lunch')
        self.assertIn(new_tag, recipe.tags.all())

    # To assign an already existent tag in database to new recipe
    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe"""

        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {'tags': [{'name': 'Lunch'}]}  # We are changing breakfast tag to lunch tag (instead of creating a new tag)
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())


    def test_clear_recipe_tags(self):
        """Test clearing a recipes tags"""

        tag = Tag.objects.create(user=self.user, name='Dessert')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags': []}  
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)



    # NOTE: >> vv Tests Involving Ingredients

    def test_create_recipe_with_new_ingredients(self):
        """Test creating a recipe with new ingredients"""

        payload = {
            'title': 'Cauliflower Tacos',
            'time_minutes': 60,
            'price': Decimal('4.30'),
            'ingredients': [{'name': 'Cauliflower'}, {'name': 'Salt'}],
        }

        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)

        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    
    def test_create_recipe_with_existing_ingredients(self):
        """Test creating a new recipe with existing ingredient"""

        ingredient = Ingredient.objects.create(user=self.user, name='Lemon')
        payload = {
            'title': 'Vietnamese Soup',
            'time_minutes': 25,
            'price': '2.55',
            'ingredients': [{'name': 'Lemon'}, {'name': 'Fish Sauce'}],
        }

        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient, recipe.ingredients.all())

        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)


    def test_create_ingredient_on_update(self):
        """Test creating an ingredient when updating a recipe"""

        recipe = create_recipe(user=self.user)

        payload = {'ingredients': [{'name': 'Limes'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(user=self.user, name='Limes')
        self.assertIn(new_ingredient, recipe.ingredients.all())


    def test_update_recipe_assign_ingredient(self):
        """Test assigning an existing ingredient when updating a recipe"""

        ingredient1 = Ingredient.objects.create(user=self.user, name='Pepper')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        ingredient2 = Ingredient.objects.create(user=self.user, name='Chili')
        payload = {'ingredients': [{'name': 'Chili'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())


    def test_clear_recipe_ingredients(self):
        """Test clearing a recipes ingredients"""

        ingredient = Ingredient.objects.create(user=self.user, name='Garlic')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload = {'ingredients': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_filter_by_tags(self):
        """Test filtering recipes by tags"""

        r1 = create_recipe(user=self.user, title='Thai Vegetable Curry')
        r2 = create_recipe(user=self.user, title='Aubergine with Tahini')
        tag1 = Tag.objects.create(user=self.user, name='Vegan')
        tag2 = Tag.objects.create(user=self.user, name='Vegetarian')
        r1.tags.add(tag1)
        r2.tags.add(tag2)
        r3 = create_recipe(user=self.user, title='Fish and Chips') # Recipe has no tags

        params = {'tags': f'{tag1.id},{tag2.id}'}  # Passing tags as comma separated string
        res = self.client.get(RECIPES_URL, params)
        # ^ Making request to filter by tags.

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)  # We are not expecting `s3` to be in the response.

    def test_filter_by_ingredients(self):
        """Test filtering recipes by ingredients"""

        r1 = create_recipe(user=self.user, title='Posh Beans on Toast')
        r2 = create_recipe(user=self.user, title='Chicken Cacciatore')
        in1 = Ingredient.objects.create(user=self.user, name='Feta Cheese')
        in2 = Ingredient.objects.create(user=self.user, name='Chicken')
        r1.ingredients.add(in1)
        r2.ingredients.add(in2)
        r3 = create_recipe(user=self.user, title='Red Lentil Daal') # Recipe has no ingredients

        params = {'ingredients': f'{in1.id},{in2.id}'}  # Passing ingredients as comma separated string
        res = self.client.get(RECIPES_URL, params)
        # ^ Making request to API with filter by ingredients.

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)  # We are not expecting `s3` to be in the response.


class ImageUploadTests(TestCase):
    """Tests for the image upload API"""

    def setUp(self):
        # ^ Runs before the tests
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'password123',
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)


    def tearDown(self):
        self.recipe.image.delete()  # Deletes the image that was created during tests.
        # ^ tearDown() is similar to setUp()
        # BUT, it runs AFTER the tests.


    def test_upload_image(self):
        """Test uploading an image to a recipe"""

        url = image_upload_url(self.recipe.id)
        # ^ url = /api/recipe/{id}/image/

        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            # Creating a Temporary image File
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')  # Saving the image to the Temporary File i.e. image_file
            image_file.seek(0)  # Seek back to beginning of file
            payload = {'image': image_file}  # Simulating a multipart form
            res = self.client.post(url, payload, format='multipart')
            # It is best practice to upload images using `multipart` forms

        # After `with`, the Temporary File is cleaned automatically

        self.recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""

        url = image_upload_url(self.recipe.id)
        payload = {'image': 'notanimage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)