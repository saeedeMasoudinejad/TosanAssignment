import os
import random
from decimal import Decimal, ROUND_DOWN

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from core.base_models import BaseModelClass
from django.contrib.auth.models import User

from core.choice_type_fields import TransactionStatusChoice
from core.settings import INITIAL_WALLET_BALANCE, MAX_TRANSFERS_VALUE_PER_DAY, MAX_TRANSFERS_PER_DAY
from core.utils import convertor


class Wallet(BaseModelClass):
    # To prevent computational errors, we consider numbers as integers and only convert them to decimal for display
    # Assuming that balances will not exceed four decimal places.
    # NOTE: Don't implement the charge the wallet,Just set the default value.
    _balance = models.BigIntegerField(
        default=INITIAL_WALLET_BALANCE,
        validators=[MinValueValidator(0), ],
        null=False,
        blank=False
    )
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

    @property
    def balance(self):
        return convertor(
            self._balance,
            'decimal'
        )

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
    transaction_number = models.CharField(
        max_length=8,
        unique=True,
        null=False,
        blank=False,
    )
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
    _amount = models.BigIntegerField(
        null=False,
        blank=False,
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

    @property
    def amount(self):
        return convertor(
            self._amount,
            'decimal'
        )

    @classmethod
    def is_daily_transfer_limit_exceeded(cls, origin_wallet, amount):
        today = timezone.now().date()
        daily_transfers = cls.objects.filter(
            origin=origin_wallet,
            created_at__date=today,
            status=TransactionStatusChoice.COMPLETE
        )
        total_count = daily_transfers.count()
        total_amount = daily_transfers.aggregate(
            models.Sum('_amount')
        )['_amount__sum'] or 0
        max_transfers_per_day = MAX_TRANSFERS_PER_DAY
        max_transfer_value_per_day = MAX_TRANSFERS_VALUE_PER_DAY
        if total_count >= max_transfers_per_day or \
                total_amount + amount > max_transfer_value_per_day:
            return True
        return False

    def save(self, *args, **kwargs):
        if not self.transaction_number:
            self.transaction_number = self.generate_unique_number()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = (
            '-updated_at',
        )

    def __str__(self):
        return f'{self.origin.owner.username} - {self.destination.owner.username} - {self.transaction_number}'
