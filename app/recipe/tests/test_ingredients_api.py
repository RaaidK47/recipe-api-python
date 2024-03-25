"""
Test Ingrediets API
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from core.models import Recipe

from recipe.serializers import IngredientSerializer

from decimal import Decimal

INGREDIENTS_URL = reverse('recipe:ingredient-list')  #  URL of API

def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user"""
    return get_user_model().objects.create_user(email=email, password=password)


def detail_url(ingredient_id):
    """Create and return a ingredient detail url"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


class PublicIngredientsApiTests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):   
    """Test authenticated API requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients"""

        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Vanilla')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')  # Order by Reverse Name Order
        # ^Making Query to DB

        serializer = IngredientSerializer(ingredients, many=True)  # Serialize result from Query

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  # Comparing Serialized Query and HTTP Response

    def test_ingredients_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user"""

        user2 = create_user(email='user2@example.com')
        Ingredient.objects.create(user=user2, name='Salt')  # Create a Ingredient for Non Authenticated User

        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')  # Create a Tag for Authenticated User
        res = self.client.get(INGREDIENTS_URL)  # Retreiving Tags

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)  # Check that only 1 results is returned (Do not expect for firts (user2) ingredient to return)
        self.assertEqual(res.data[0]['name'], ingredient.name)  # First Result i.e. [0], the name should be ingredient.name for Authenticated User
        self.assertEqual(res.data[0]['id'], ingredient.id)

    
    def test_update_ingredient(self):
        """Test updating a ingredient"""

        ingredient = Ingredient.objects.create(user=self.user, name='Cilantro')

        payload = {'name': 'Coriander'}

        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()  # Refresh DB after PATCH request
        self.assertEqual(ingredient.name, payload['name'])
        self.assertEqual(ingredient.user, self.user)

    def test_delete_ingredient(self):
        """Test deleting a ingredient"""

        ingredient = Ingredient.objects.create(user=self.user, name='Lettuce')

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)  # Retreiving all Tags of Authenticated User
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test Listing ingredients by those assigned to recipes"""

        Ingredient1 = Ingredient.objects.create(user=self.user, name='Apples')
        Ingredient2 = Ingredient.objects.create(user=self.user, name='Turkey')
        recipe = Recipe.objects.create(
            title='Apple Crumble',
            time_minutes=5,
            price=Decimal('5.50'),
            user=self.user
        )
        recipe.ingredients.add(Ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        # Getting only ingredients that are assinged to some recipes.

        s1 = IngredientSerializer(Ingredient1)
        s2 = IngredientSerializer(Ingredient2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients returns a unique list"""

        ing = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Cheese')

        recipe1 = Recipe.objects.create(
            title='Eggs benedict',
            time_minutes=30,
            price=Decimal('12.00'),
            user=self.user
        )

        recipe2 = Recipe.objects.create(
            title='Green eggs on toast',
            time_minutes=20,
            price=Decimal('5.00'),
            user=self.user
        )
        
        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        
        self.assertEqual(len(res.data), 1 ) # Making sure that ingredient is returned only once.