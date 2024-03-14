"""
Views for the user API. (This uses our Serializers)
"""

from rest_framework import generics  # REST framework handles logic needed for creating objects in Database
# ^ It provides some base classes that we can configure for our views that will handle request in standardized way
# ^ It also provide us ability to override some of the behaviour as per our need.

from rest_framework.authtoken.views import ObtainAuthToken  # Builtin code of Django for Creating Tokens
from rest_framework.settings import api_settings


from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    # ^CreateAPIView handles HTTP POST requests to create a new object.
    """Create a new user in the system."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):  # ObtainAuthToken view uses the username and password instead of email and password. 
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer  # Customizing Serializer to use custom Serializer that we created
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES  # (Optional)
    # ^To Show Browesable API