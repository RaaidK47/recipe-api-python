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
         
        res = self.client.post(CREATE_USER_URL, payload)  # Make a POST request and Pass in the Payload

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
