from rest_framework import serializers

from finance.models import Wallet


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
