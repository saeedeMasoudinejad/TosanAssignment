from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User


class SignupTests(APITestCase):
    def setUp(self):
        User.objects.create_user(
            username='test_user_2',
            password='test_password_2'
        )

    def test_signup(self):
        url = reverse('signup')
        data = {
            'username': 'test_user_1',
            'password': 'test_password_1'
        }
        response = self.client.post(
            url,
            data,
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertTrue(
            'refresh' in response.data
        )
        self.assertTrue(
            'access' in response.data
        )

    def test_signup_existing_username(self):
        url = reverse('signup')
        data = {
            'username': 'test_user_2',
            'password': 'test_password_2'
        }
        response = self.client.post(
            url,
            data,
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_signup_None_username(self):
        url = reverse('signup')
        data = {
            'username': ' ',
            'password': 'test_password_1'
        }
        response = self.client.post(
            url,
            data,
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
