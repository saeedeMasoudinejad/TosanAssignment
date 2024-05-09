import os

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Wallet


class WalletCreationTest(APITestCase):
    def setUp(self):
        self.user_1 = User.objects.create_user(
            username='testuser_1',
            password='12345'
        )
        self.user_2 = User.objects.create_user(
            username='testuser_2',
            password='12345'
        )

    def test_wallet_creation_unauthenticated(self):
        url = reverse('wallet-creation')
        response = self.client.post(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )
        self.assertEqual(
            Wallet.objects.count(),
            0
        )

    def test_wallet_creation(self):
        self.client.force_authenticate(
            user=self.user_1
        )
        url = reverse('wallet-creation')
        response = self.client.post(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(
            Wallet.objects.count(),
            1
        )
        wallet = Wallet.objects.first()
        self.assertEqual(
            wallet.owner,
            self.user_1
        )
        self.assertEqual(
            wallet.balance,
            int(os.environ['WALLET_BALANCE'])
        )

    def test_wallet_creation_user_has_wallet(self):
        self.client.force_authenticate(user=self.user_2)
        url = reverse('wallet-creation')
        response_1 = self.client.post(url)
        response_2 = self.client.post(url)
        self.assertEqual(
            response_1.status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(
            response_2.status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(
            Wallet.objects.count(),
            2
        )
        existing_wallet = Wallet.objects.first()
        new_wallet = Wallet.objects.last()
        self.assertNotEquals(
            existing_wallet._wallet_number,
            new_wallet._wallet_number
        )

    def test_wallet_creation_set_owner(self):
        self.client.force_authenticate(user=self.user_1)
        url = reverse('wallet-creation')
        response = self.client.post(
            url,
            {'owner': self.user_1.id + 1},
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertFalse(Wallet.objects.filter(
            owner_id=self.user_1.id + 1).exists()
                         )
