import os
import random

from django.db import models

from core.base_models import BaseModelClass
from django.contrib.auth.models import User


class Wallet(BaseModelClass):
    # To prevent computational errors, we consider numbers as integers and only convert them to decimal for display
    # (assuming that balances will not exceed four decimal places).
    # NOTE: Don't implement the charge the wallet,Just set the default value.
    # TODO: type of this field and way of convert should be correct
    balance = models.PositiveIntegerField(
        default=1000000
    )
    owner = models.ForeignKey(
        to=User,
        on_delete=models.PROTECT,
        related_query_name='wallet',
        related_name='users'
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
    def real_balance(self):
        return self.balance * 10 ^ int(os.environ['DECIMAL_PLACES'])

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
