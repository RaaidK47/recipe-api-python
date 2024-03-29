"""
Tests for the User API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')  # user=app  create=endpoint
TOKEN_URL = reverse('user:token')  # user=app  token=endpoint
ME_URL = reverse('user:me')  # user=app  me=endpoint


# Helper Function to create a user
def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    # ^Public = UnAuthenticated Requests
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()
        
    def test_create_user_success(self):
        """Test creating a user is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        # ^(Dictionary) Test Payload to POST to API for the test
         
        res = self.client.post(CREATE_USER_URL, payload)  # Make a POST request and Pass in the Payload (To Create a new user)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  # Assert the Status Code is 201 i.e. Created
        user = get_user_model().objects.get(email=payload['email'])  # Retreives the Object from Database that we passed in as Payload
        # ^Validate that object is actually created in the database

        self.assertTrue(user.check_password(payload['password']))
        # ^Validate that the password is hashed and stored correctly in the database

        self.assertNotIn('password', res.data)
        # ^Assert that the password is not returned in the response data (To Test Security)


    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'XXXXXXXXXXX',
            'name': 'Test Name',
        }
        create_user(**payload)  # Create the user first
        # ^Create the user first before making the POST request to the API
        # ^This is to ensure that the user with the same email already exists in the database

        res = self.client.post(CREATE_USER_URL, payload)  # Make a POST request and Pass in the Payload
        # ^This should fail as the user already exists in the database

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # Assert the Status Code is 400 i.e. Bad Request

    
    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)  # Make a POST request and Pass in the Payload

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # Assert the Status Code is 400 i.e. Bad Request
        
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()  # Checks if the user with the same email exists in the database
        # ^Make sure that the user is not created (Returns a Boolean, ifExist > True)

        self.assertFalse(user_exists)  # Assert that the user does not exist in the database

    
    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'XXXXXXXXXXXXXXXXXXXXX',
        }
        create_user(**user_details)  # Create the user first

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)  # Make a POST request and Pass in the Payload

        self.assertIn('token', res.data)  # Assert that the token is returned in the response data
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Assert the Status Code is 200 i.e. OK


    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""
        create_user(email='test@example.com', password='goodpass')  # Create the user first

        payload = {'email': 'test@example.com', 'password': 'badpass'}
        res = self.client.post(TOKEN_URL, payload)  # Make a POST request and Pass in the Payload

        self.assertNotIn('token', res.data)  # Assert that the token is not returned in the response data (Token not Generated due to bad credentials)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # Assert the Status Code is 400 i.e. Bad Request

    
    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""
        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)  # Make a POST request and Pass in the Payload

        self.assertNotIn('token', res.data)  # Assert that the token is not returned in the response data (Token not Generated due to blank password)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # Assert the Status Code is 400 i.e. Bad Request

    
    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(ME_URL)  # Make a GET request (Unathorized Request)
        # ^You are not authorized to used endpoint if you are not authenticated

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)  # Assert the Status Code is 401 i.e. Unauthorized


# v Private = Authorized Requests
# setUp method creates an authenticated user
class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='XXXXXXXXXXX',
            name='Test Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)  # Authenticate the user before making any requests (Forced)
        # Force Authentication (For Testing Purpose only)
        # Any request from client from now on will be authenticated

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""
        res = self.client.get(ME_URL)  # Make a GET request (Authorized Request)
        # ^Retreive the detail of current authenticated user

        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Assert the Status Code is 200 i.e. OK
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })  # Assert the response data is the same as the user object

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint."""
        # Making sure that HTTP POST is disabled for ME Endpoint
        # HTTP POST is only used when you are creating Object in System
        # ME is used for modifying only, (not creating new objects in the system)

        res = self.client.post(ME_URL, {})  # Make a POST request (Authorized Request)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)  # Assert the Status Code is 405 i.e. Method Not Allowed

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""

        payload = {'name': 'Updated Name', 'password': 'newpass123'}

        res = self.client.patch(ME_URL, payload)  # Make a PATCH request (Authorized Request)
        # The HTTP PATCH request method applies partial modifications to a resource.
        # PATCH is somewhat analogous to the "update" concept found in CRUD

        self.user.refresh_from_db()  # Refresh the user object from the database
        # ^Refresh the user object from the database after making the PATCH request

        self.assertEqual(self.user.name, payload['name'])  # Assert that the name is updated in the user object
        self.assertTrue(self.user.check_password(payload['password']))  # Assert that the password is hashed and stored correctly in the database
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Assert the Status Code is 200 i.e. OK
        # ^Assert that the name is updated in the user object
        # ^Assert that the password is hashed and stored correctly in the database
        # ^Assert the Status Code is 200 i.e. OK

