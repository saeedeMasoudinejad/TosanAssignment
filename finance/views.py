import os
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import F, Q
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from core.choice_type_fields import TransactionStatusChoice, TransactionTypeChoice
from core.message_text import MessageText
from core.utils import convertor
from finance.models import Wallet, Transaction
from finance.serializers import TransactionWriteOnlySerializer, \
    TransactionReadOnlyModelSerializer, WalletModelSerializer
from django.db import transaction, IntegrityError, OperationalError


class WalletCreation(
    mixins.CreateModelMixin,
    GenericViewSet
):
    serializer_class = WalletModelSerializer
    queryset = Wallet.objects.all()

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    # def create(self, request, *args, **kwargs):
    #     request.data['owner'] = self.request.user.id
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     return super(WalletCreation, self).create(request, *args, **kwargs)

    # @action(
    #     detail=False,
    #     methods=['GET'],
    # )
    # def wallet_creation(self, request, *args, **kwargs):
    #     # This api does not require any input parameters for creating a wallet,
    #     # and there are no plans for further development.
    #     # The Single Responsibility Principle is implemented with the GET request.
    #     wallet = Wallet.objects.create(owner=request.user)
    #     serializer = self.get_serializer(wallet)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)


class TransactionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    serializer_class = TransactionWriteOnlySerializer
    queryset = Transaction.objects.all()

    def get_queryset(self):
        if self.action == 'list':
            return Transaction.objects.filter(
                Q(origin__owner=self.request.user) |
                Q(destination__owner=self.request.user)
            )
        return self.queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return TransactionReadOnlyModelSerializer
        return self.serializer_class

    # @action(detail=False, methods=['POST'])
    # def deposit(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     data = serializer.validated_data
    #     amount = data['amount']
    #     sender_wallet_number = data['sender_wallet_number']['wallet_number']
    #     receiver_wallet_number = data['receiver_wallet_number']['wallet_number']
    #     try:
    #         sender_wallet = Wallet.objects.get(
    #             owner=self.request.user.id,
    #             _wallet_number=sender_wallet_number
    #         )
    #     except Wallet.DoesNotExist:
    #         raise NotFound(MessageText.WalletNumberIsNotBelong)
    #     try:
    #         receiver_wallet = Wallet.objects.get(
    #             _wallet_number=receiver_wallet_number
    #         )
    #     except Wallet.DoesNotExist:
    #         raise NotFound(MessageText.WalletNumberNotFound)
    #     with transaction.atomic():
    #         finance_transaction = Transaction.objects.create(
    #             sender_wallet=sender_wallet,
    #             receiver_wallet=receiver_wallet,
    #             amount=amount
    #         )
    #         if amount > sender_wallet.balance or Transaction.is_daily_transfer_limit_exceeded(sender_wallet,
    #                                                                                           amount):
    #             # TODO: call the refund method
    #             finance_transaction.status = TransactionStatusChoice.FAILED
    #             finance_transaction.save()
    #             return Response(
    #                 exception=MessageText.DailyTransferLimitExceeded,
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
    #         else:
    #             sender_wallet.balance -= amount
    #             receiver_wallet.balance += amount
    #             sender_wallet.save()
    #             receiver_wallet.save()
    #             finance_transaction.status = TransactionStatusChoice.COMPLETE
    #             finance_transaction.save()
    #             return Response(
    #                 serializer.data,
    #                 status=status.HTTP_200_OK
    #             )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        amount = convertor(data['amount'],'int')
        origin_wallet_number = data['origin_wallet_number']
        destination_wallet_number = data['destination_wallet_number']

        try:
            origin_wallet = Wallet.objects.select_for_update().get(
                owner=self.request.user.id,
                _wallet_number=origin_wallet_number
            )
        except Wallet.DoesNotExist:
            raise NotFound(
                MessageText.WalletNumberIsNotBelong
            )

        try:
            destination_wallet = Wallet.objects.select_for_update().get(
                _wallet_number=destination_wallet_number
            )
        except Wallet.DoesNotExist:
            raise NotFound(MessageText.WalletNumberNotFound)

        if amount > origin_wallet._balance or Transaction.is_daily_transfer_limit_exceeded(origin_wallet, amount):
            status_choice = TransactionStatusChoice.FAILED
            exception_message = MessageText.DailyTransferLimitExceeded
        else:
            status_choice = TransactionStatusChoice.PENDING
            exception_message = None

        with transaction.atomic():
            try:
                finance_transaction = Transaction.objects.create(
                    origin=origin_wallet,
                    destination=destination_wallet,
                    _amount=amount,
                    status=status_choice,
                    transaction_type=data['transaction_type']
                )
            except (IntegrityError, OperationalError):
                # Transaction creation failed due to concurrent transaction
                raise IntegrityError("Concurrent transaction, please try again.")

            if exception_message:
                finance_transaction.status = TransactionStatusChoice.FAILED
                finance_transaction.save()
                return Response(
                    {
                        'exception': exception_message
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            origin_wallet._balance = F('_balance') - amount
            destination_wallet._balance = F('_balance') + amount
            origin_wallet.save()
            destination_wallet.save()
            finance_transaction.status = TransactionStatusChoice.COMPLETE
            finance_transaction.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
