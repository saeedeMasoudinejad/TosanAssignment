from decimal import Decimal

from unittest.mock import patch

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

from core.choice_type_fields import TransactionTypeChoice, TransactionStatusChoice
from core.settings import INITIAL_WALLET_BALANCE
from finance.models import Wallet, Transaction


class TransactionAPITest(APITestCase):
    def setUp(self):
        # self.client = APIClient()
        self.user_1 = User.objects.create_user(
            username='testuser_1',
            password='testpassword'
        )
        self.user_2 = User.objects.create_user(
            username='testuser_2',
            password='testpassword'
        )

        # Creating wallets for the user
        self.origin_wallet = Wallet.objects.create(owner=self.user_1)
        self.destination_wallet = Wallet.objects.create(owner=self.user_2)

    def test_create_transaction_unauthorized(self):
        url = reverse('transaction-list')
        response = self.client.post(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_transaction(self):
        url = reverse('transaction-list')
        self.client.force_authenticate(user=self.user_1)
        data = {
            'origin_wallet_number': self.origin_wallet.wallet_number,
            'destination_wallet_number': self.destination_wallet.wallet_number,
            'amount': 100000,
            'transaction_type': TransactionTypeChoice.DEPOSITED
        }
        response = self.client.post(url, data, format='json')
        self.origin_wallet.refresh_from_db()
        self.destination_wallet.refresh_from_db()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            Transaction.objects.count(),
            1
        )
        self.assertEqual(
            Transaction.objects.get().amount,
            100000
        )
        self.assertEqual(
            self.origin_wallet.balance,
            900000
        )
        self.assertEqual(
            self.destination_wallet.balance,
            1100000
        )
        self.assertEqual(
            Transaction.objects.get().transaction_type,
            TransactionTypeChoice.DEPOSITED
        )
        self.assertEqual(
            Transaction.objects.get().status,
            TransactionStatusChoice.COMPLETE
        )

    def test_create_transaction_with_decimal_amount(self):
        url = reverse('transaction-list')
        self.client.force_authenticate(user=self.user_1)
        data = {
            'origin_wallet_number': self.origin_wallet.wallet_number,
            'destination_wallet_number': self.destination_wallet.wallet_number,
            'amount': 850000.19,
            'transaction_type': TransactionTypeChoice.DEPOSITED
        }
        response = self.client.post(
            url,
            data,
            format='json')

        self.origin_wallet.refresh_from_db()
        self.destination_wallet.refresh_from_db()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

        self.assertEqual(
            Transaction.objects.count(),
            1)

        self.assertEqual(
            Transaction.objects.get().amount,
            Decimal('850000.19')
        )
        self.assertEqual(
            self.origin_wallet.balance,
            round(Decimal(149999.81), 2)
        )
        self.assertEqual(
            self.destination_wallet.balance,
            round(Decimal(1850000.19), 2)
        )
        self.assertEqual(
            Transaction.objects.get().transaction_type,
            TransactionTypeChoice.DEPOSITED
        )
        self.assertEqual(
            Transaction.objects.get().status,
            TransactionStatusChoice.COMPLETE
        )

    def test_create_transaction_with_negative_amount(self):
        url = reverse('transaction-list')
        self.client.force_authenticate(user=self.user_1)
        data = {
            'origin_wallet_number': self.origin_wallet.wallet_number,
            'destination_wallet_number': self.destination_wallet.wallet_number,
            'amount': -1000,
            'transaction_type': TransactionTypeChoice.DEPOSITED
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

    def test_create_transaction_with_origin_wallet_is_not_valid(self):
        url = reverse('transaction-list')
        self.client.force_authenticate(user=self.user_2)
        data = {
            'origin_wallet_number': self.origin_wallet.wallet_number,
            'destination_wallet_number': self.destination_wallet.wallet_number,
            'amount': -1000,
            'transaction_type': TransactionTypeChoice.DEPOSITED
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
        self.assertEqual(
            Transaction.objects.count(),
            0
        )
        self.assertEqual(
            self.origin_wallet._balance,
            INITIAL_WALLET_BALANCE
        )
        self.assertEqual(
            self.destination_wallet._balance,
            INITIAL_WALLET_BALANCE
        )

    def test_create_transaction_with_destination_wallet_is_not_valid(self):
        url = reverse('transaction-list')
        self.client.force_authenticate(user=self.user_1)
        data = {
            'origin_wallet_number': self.origin_wallet.wallet_number,
            'destination_wallet_number': self.origin_wallet.wallet_number,
            'amount': -1000,
            'transaction_type': TransactionTypeChoice.DEPOSITED
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
        self.assertEqual(
            Transaction.objects.count(),
            0
        )
        self.assertEqual(
            self.origin_wallet._balance,
            INITIAL_WALLET_BALANCE
        )
        self.assertEqual(
            self.destination_wallet._balance,
            INITIAL_WALLET_BALANCE
        )

    @patch(
        'finance.models.Transaction.is_daily_transfer_limit_exceeded',
        return_value=True
    )
    def test_create_transaction_with_exceed_transaction_number_per_day(
            self,
            mock_is_daily_transfer_limit_exceeded
    ):
        url = reverse('transaction-list')
        self.client.force_authenticate(user=self.user_1)
        data = {
            'origin_wallet_number': self.origin_wallet.wallet_number,
            'destination_wallet_number': self.origin_wallet.wallet_number,
            'amount': 100000,
            'transaction_type': TransactionTypeChoice.DEPOSITED
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
        self.assertEqual(
            Transaction.objects.count(),
            1
        )
        self.assertEqual(
            Transaction.objects.get().status,
            TransactionStatusChoice.FAILED
        )
