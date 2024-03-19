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

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """Create and return a recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])
    # ^This is a helper function to create a recipe detail URL
    # ^The args is a list of arguments that will be passed to the function
    # ^The first argument is the recipe_id
    # ^The second argument is the name of the view

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
