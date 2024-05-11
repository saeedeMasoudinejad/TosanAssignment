from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

from core.choice_type_fields import (
    TransactionTypeChoice,
    TransactionStatusChoice
)
from core.settings import INITIAL_WALLET_BALANCE
from finance.models import Wallet, Transaction


class RefundTransactionAPITest(APITestCase):
    def setUp(self):
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

        # Creating transaction
        self.transaction = Transaction.objects.create(
            origin=self.origin_wallet,
            destination=self.destination_wallet,
            _amount=100000,
            status=TransactionStatusChoice.COMPLETE,
            transaction_type=TransactionTypeChoice.WITHDRAWAL
        )

    def test_refund_transaction(self):
        self.client.force_authenticate(user=self.user_1)
        transaction = self.transaction
        url = reverse('transaction-refund',
                      kwargs={'pk': transaction.transaction_number}
                      )

        response = self.client.get(url)
        self.origin_wallet.refresh_from_db()
        self.destination_wallet.refresh_from_db()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            Transaction.objects.get(transaction_type=TransactionTypeChoice.REFUNDED).status,
            TransactionStatusChoice.COMPLETE
        )
        self.assertEqual(
            Transaction.objects.get(transaction_type=TransactionTypeChoice.REFUNDED).transaction_type,
            TransactionTypeChoice.REFUNDED
        )
        self.assertEqual(
            Transaction.objects.get(transaction_type=TransactionTypeChoice.REFUNDED).original_transaction,
            transaction
        )
        self.assertEqual(
            self.origin_wallet._balance,
            INITIAL_WALLET_BALANCE + transaction._amount
        )

        self.assertEqual(
            self.destination_wallet._balance,
            INITIAL_WALLET_BALANCE - transaction._amount
        )
