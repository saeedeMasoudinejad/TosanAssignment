import os
import random

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from core.base_models import BaseModelClass
from django.contrib.auth.models import User

from core.choice_type_fields import TransactionStatusChoice


class Wallet(BaseModelClass):
    # TODO:To prevent computational errors, we consider numbers as integers and only convert them to decimal for display
    # Assuming that balances will not exceed four decimal places.
    # NOTE: Don't implement the charge the wallet,Just set the default value.
    # TODO: type of this field and way of convert should be correct
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=os.environ['WALLET_BALANCE']
    )
    # temporary_balance = models.DecimalField(
    #     max_digits=10,
    #     decimal_places=2,
    #     default=os.environ['WALLET_BALANCE']
    # )
    owner = models.ForeignKey(
        to=User,
        on_delete=models.PROTECT,
        related_query_name='wallet',
        related_name='wallets'
    )

    _wallet_number = models.CharField(
        max_length=8,
        unique=True,
        null=False,
        blank=False,
    )
    is_active = models.BooleanField(
        default=True,
    )

    # @property
    # def real_balance(self):
    #     return self.balance * 10 ^ int(os.environ['DECIMAL_PLACES'])

    @staticmethod
    def generate_unique_number():
        six_digit_number = random.randint(100000, 999999)
        checksum = 10 - sum(int(digit) for digit in str(six_digit_number)) % 10
        if checksum == 10:
            checksum = 0
        eight_digit_number = int(str(six_digit_number) + str(checksum))
        return str(eight_digit_number)

    @property
    def wallet_number(self):
        return self._wallet_number

    def save(self, *args, **kwargs):
        if not self.wallet_number:
            self._wallet_number = self.generate_unique_number()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'

    def __str__(self):
        return f'{self.owner} - {self.wallet_number}'


class Transaction(BaseModelClass):
    origin = models.ForeignKey(
        to=Wallet,
        related_name='origin_transactions',
        related_query_name='origin_transaction',
        on_delete=models.PROTECT
    )
    destination = models.ForeignKey(
        to=Wallet,
        related_name='destination_transactions',
        related_query_name='destination_transaction',
        on_delete=models.PROTECT)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1000)]
    )
    status = models.CharField(
        max_length=10,
        choices=TransactionStatusChoice.choices,
        default=TransactionStatusChoice.PENDING
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionStatusChoice.choices
    )


    @classmethod
    def is_daily_transfer_limit_exceeded(cls, sender_wallet, amount):
        today = timezone.now().date()
        daily_transfers = cls.objects.filter(
            sender_wallet=sender_wallet,
            created_at__date=today,
            status=TransactionStatusChoice.COMPLETE
        )
        total_count = daily_transfers.count()
        total_amount = daily_transfers.aggregate(models.Sum('amount'))['amount__sum'] or 0
        max_transfers_per_day = int(os.environ.get('MAX_TRANSFERS_PER_DAY'))
        max_transfer_value_per_day = int(os.environ.get('MAX_TRANSFERS_VALUE_PER_DAY'))
        if total_count >= max_transfers_per_day or total_amount + amount > max_transfer_value_per_day:
            return True
        return False
