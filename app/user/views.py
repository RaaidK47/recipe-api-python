"""
Views for the user API. (This uses our Serializers)
"""

from rest_framework import generics  # REST framework handles logic needed for creating objects in Database
# ^ It provides some base classes that we can configure for our views that will handle request in standardized way
# ^ It also provide us ability to override some of the behaviour as per our need.

from rest_framework import authentication  # Builtin code of Django for Authentication
from rest_framework import permissions  # Builtin code of Django for Permissions

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

class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    # generics.RetrieveUpdateAPIView handles HTTP GET and HTTP PUT/PATCH requests for retrieving and updating an object. (from Database)

    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]  # Check whether the user is authenticated
    permission_classes = [permissions.IsAuthenticated]  # Check whether the user has the required permissions (What user is allowed to do)
    # ^In our case the user has to be only Authenticated to use this API
    # ^We can also use `permissions.IsAdminUser` to check whether the user is an admin user

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user  # ^This will return the user that is authenticated
        # ^We can also use `self.request.user.id` to get the user id
        # ^We can also use `self.request.user.email` to get the user email
        # ^We can also use `self.request.user.username` to get the user username
        # ^We can also use `self.request.user.first_name` to get the user first_name
        # ^We can also use `self.request.user.last_name` to get the user last_name
        # ^We can also use `self.request.user.is_superuser` to get the user is_superuser
        # ^We can also use `self.request.user.is_staff` to get the user is_staff
    
        # Sequence ==> GET Request (ME) > call get_object() > return the user that is authenticated > run it through serializer_class() > return the result to API