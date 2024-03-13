"""
Database Models
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,  # contains the functionality for the authentication system, but not any fields.
    BaseUserManager,  # contains the functionality for the permissions feature of Django, and it also contains any fields that are needed for the permissions feature. # noqa: E501
    PermissionsMixin,
)


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
