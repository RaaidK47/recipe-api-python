"""
Database Models
"""

from django.conf import settings  # Used in Recipe Model

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,  # contains the functionality for the authentication system, but not any fields.
    BaseUserManager,  # contains the functionality for the permissions feature of Django, and it also contains any fields that are needed for the permissions feature. # noqa: E501
    PermissionsMixin,
)

import uuid 
import os

# Function to Generate Path of Image that we upload
def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image"""

    ext = os.path.splitext(filename)[1]  # Get the extension of the file
    filename = f"{uuid.uuid4()}{ext}"  # Generate a random UUID and append the extension to the filename

    return os.path.join("uploads", "recipe", filename)  # Join the path components to form a complete file path. # noqa: E501
    # ^This function will be called when the recipe image is uploaded. 
    # To ensures that the string is created in the appropriate format for the OS that we're running the code on. 
    # ^ Instead to manually typing the PATH.
   

class UserManager(BaseUserManager):
    """Manager for users"""

    def create_user(self, email, password=None, **extra_fields):  # extra_fields > we can provide keyword arguments # noqa: E501
        """Create, save and return a new user"""
        if not email:
            raise ValueError("User must have an email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)  # Normalize the email address and store it in the database. # noqa: E501
        user.set_password(password)  # Hash the password and store it in the database - Actual Password is preserved
        # ^When logging in, the password is hashed and compared to the hashed password in the database.
        user.save(using=self._db)  # Save the user to the database using the specified database connection. Can add multiple databases to the project # noqa: E501

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser"""
        user = self.create_user(email, password)  # Create a new user using above method # noqa: E501
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user
        # is_staff is a boolean field that is set to True by default.
        # It is used to determine whether the user has the ability to log into the Django admin site.
        # is_superuser is a boolean field that is set to True by default.


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""

    email = models.EmailField(max_length=255, unique=True)  # All emails have to be ubique in system
    name = models.CharField(max_length=255)  
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Can user login to Django Admin

    objects = UserManager()  # UserManager is a class that inherits from BaseUserManager and provides methods for creating and managing users. # noqa: E501

    USERNAME_FIELD = "email"

# Add user model at end of settings.py file as below (IMPORTANT)
# AUTH_USER_MODEL = 'core.User'
# Also make sure that 'core' app is in INSTALLED_APPS in settings.py file


class Recipe(models.Model):  # base Model Class
    """Recipe object"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Referencing a string from settings.py file
        on_delete=models.CASCADE,  # If the user is deleted, the assosiated recipes should also be deleted.
        # Compliance with Data Compliance rules 
    )
    # ^ForeignKey is a relationship between two models.


    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)  # blank=True means that the field is optional and can be left blank.
    # TextField hold more content and multiple line of content
    # In some databases, TextField is slow to load than CharField. (Hence not used everywhere)

    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)

    tags = models.ManyToManyField("Tag")  # ManyToManyField is a relationship between two models that allows a many-to-many relationship between the two models. # noqa: E501
    # ^Many different recipes can have many different Tags
    # any of our tags can be associated to any of our recipes and any of our recipes can be associated to any of our tags.

    ingredients = models.ManyToManyField("Ingredient")  # ^Same as above

    image = models.ImageField(null=True, upload_to=recipe_image_file_path)  

    def __str__(self):
        return self.title
        # ^This will return the title of the recipe (When object is printed out as a string i.e. str(recipe) in test_create_recipe)
        # ^This will be used in the admin panel to display the title of the recipe in the list of recipes.
        # ^If not specified, the ID of object will be shown in Django Admin. (Not very useful)
    

class Tag(models.Model):
    """Tag for filtering recipes"""  # < Primary usage of Tag

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    """Ingredient for recipes"""

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
 

