# Generated by Django 5.0.4 on 2024-05-10 10:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0009_remove_transaction_amount_remove_wallet_balance_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='_balance',
            field=models.BigIntegerField(default='100000000', validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
