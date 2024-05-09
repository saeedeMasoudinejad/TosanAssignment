from django.core.validators import MinValueValidator
from rest_framework import serializers

from finance.models import Wallet, Transaction


class WalletModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = (
            'owner',
            'balance',
            'wallet_number'
        )
        read_only_fields = (
            'balance',
            'wallet_number',
        )


class TransactionWriteOnlySerializer(serializers.Serializer):
    sender_wallet_number = serializers.CharField()
    receiver_wallet_number = serializers.CharField()
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1000)]
    )


class TransactionReadOnlyModelSerializer(serializers.ModelSerializer):
    sender_wallet = WalletModelSerializer(read_only=True)
    receiver_wallet = WalletModelSerializer(read_only=True)
    # transaction_type = serializers.SerializerMethodField()
    class Meta:
        model = Transaction
        fields = (
            'updated_at',
            'sender_wallet',
            'receiver_wallet',
            'amount',
            # 'transaction_type',
        )

    # def get_transaction_type(self,
    #                          obj)
    #     if obj.sender_wallet == self.context['request'].user:
    #         transaction_type = 'withdrew'
    #     else