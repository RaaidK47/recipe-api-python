"""
Tests for Django Admin Modifications
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):
    """Tests for Django Admin"""

    # setUp() runs before any single test that we add
    def setUp(self):
        """Create user and client"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
        )
        self.client.force_login(self.admin_user)  # Force authentication to this user.
        # ^Every request we make through this client is going to be authenticated with this user that we've created.
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='XXXXXXXXXXX',
            name='Test User'
        )

    def test_users_list(self):
        """Test that users are listed on page"""
        url = reverse('admin:core_user_changelist')  # get URL of the page that shows the list of users.
        res = self.client.get(url)  # Make a GET request to that URL. Clients will be forced login and authenticated as login user

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test the edit user page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])  # Passing user ID 
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Making sure that page loads successfully

    def test_create_user_page(self):
        """Test the create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        # ^This is a test that the create user page loads successfully.
