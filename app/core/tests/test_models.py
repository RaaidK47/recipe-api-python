"""
Tests for Models
"""

from decimal import Decimal  # Used to store one value of Recipe Object

from django.test import TestCase
from django.contrib.auth import get_user_model  # Get reference to in-built user model

from core import models  # Get reference to custom models


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)  # Create a new user object and return it.
    # ^Creating a new user object and returning it.
   

class ModelTests(TestCase):
    """Test Models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'XXXXXXXXXXX'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))  # Checking Password throught the Hashing System

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],  # ['input email' , 'expected / normalized email']
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')  # Pass = sample123 
            self.assertEqual(user.email, expected)     
            # ^Making sure that user.email is equal to expected after the user is created no matter the input email address

    # Making sure that an email address is provided when creating a user
    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')  # Pass = test123

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )
        self.assertTrue(user.is_superuser) 
        self.assertTrue(user.is_staff)  # Making sure that the superuser is a staff member


    def test_create_recipe(self):
        """Test creating a recipe is successful."""

        # Creating a test user
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        recipe = models.Recipe.objects.create(
            user=user,  # User the recipe belongs to
            title='Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),  # For real-world financial app (which involves calculations), it is recommended to use integer for Price
            # Decimal is more accurate that in-built float data type

            description='Sample recipe description.',
        )

        self.assertEqual(str(recipe), recipe.title)


    def test_create_tag(self):
        """Test creating a tag is successful"""

        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)