from django.core.validators import MinValueValidator
from rest_framework import serializers

from core.choice_type_fields import TransactionTypeChoice
from finance.models import Wallet, Transaction


class WalletModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = (
            'balance',
            'wallet_number',
            'is_active',
        )
        read_only_fields = (
            'balance',
            'wallet_number',
            'is_active',
        )


class TransactionWriteOnlySerializer(serializers.Serializer):
    origin_wallet_number = serializers.CharField(required=True)
    destination_wallet_number = serializers.CharField(required=True)
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(1000)]
    )
    transaction_type = serializers.ChoiceField(
        choices=[
            TransactionTypeChoice.DEPOSITED,
            TransactionTypeChoice.WITHDRAWAL
        ],
        required=True
    )


class TransactionReadOnlyModelSerializer(serializers.ModelSerializer):
    origin = WalletModelSerializer(read_only=True)
    destination = serializers.PrimaryKeyRelatedField(source='destination.wallet_number', read_only=True)
    transaction_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Transaction
        fields = (
            'transaction_number',
            'updated_at',
            'origin',
            'destination',
            'amount',
            'transaction_type',
            'status'
        )

    def get_transaction_type(self, obj):
        if 'wallet_number' in self.context and \
                obj.transaction_type != TransactionTypeChoice.REFUNDED:
            if obj.origin.wallet_number == self.context['wallet_number']:
                transaction_type = TransactionTypeChoice.WITHDRAWAL
            else:
                transaction_type = TransactionTypeChoice.DEPOSITED
        else:
            transaction_type = obj.transaction_type
        return transaction_type
