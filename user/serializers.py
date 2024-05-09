from django.contrib.auth.models import User
from rest_framework import serializers

from finance.serializers import WalletModelSerializer


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        read_only_fields = (
            'id',
        )


class ProfileReadOnlySerializer(serializers.ModelSerializer):
    wallets = WalletModelSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'username',
            'wallets'
        )
