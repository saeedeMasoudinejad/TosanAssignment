from django.db import models


class TransactionStatusChoice(models.TextChoices):
    PENDING = 'pending', 'Pending'
    COMPLETE = 'complete', 'Complete'
    FAILED = 'failed', 'Failed'


class TransactionTypeChoice(models.TextChoices):
    WITHDRAWAL = 'withdrawal', 'Withdrawal'
    DEPOSITED = 'deposited', 'Deposited'
    REFUNDED = 'refunded', 'Refunded'
