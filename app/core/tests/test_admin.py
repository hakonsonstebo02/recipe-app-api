import email
from urllib import response
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
"""Allow us to generate urls"""
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@dev.com', password='password123')
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='test@dev.com', password='password123', name='Test user full name')

    def test_users_listed(self):
        """Test that users are listed"""
        url = reverse("admin:core_user_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    def test_user_change_page(self):
        """Test that the user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:core_user_add')
        response = self.client.get(url)
        assert response.status_code == 200