import random

from django.db import models


class BaseModelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(is_deleted=True)


class BaseModelClass(models.Model):
    objects = BaseModelManager()
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=False,
                                      blank=False,
                                      db_index=True)
    updated_at = models.DateTimeField(
        auto_now=True
    )
    is_deleted = models.BooleanField(
        default=False
    )

    @staticmethod
    def generate_unique_number():
        six_digit_number = random.randint(100000, 999999)
        checksum = 10 - sum(int(digit) for digit in str(six_digit_number)) % 10
        if checksum == 10:
            checksum = 0
        eight_digit_number = int(str(six_digit_number) + str(checksum))
        return str(eight_digit_number)

    class Meta:
        abstract = True
