from django.db.models import F, Q
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.choice_type_fields import (
    TransactionStatusChoice,
    TransactionTypeChoice
)
from core.message_text import MessageText
from core.paginations import CustomPaginator
from core.utils import convertor
from finance.models import (
    Wallet,
    Transaction
)
from finance.permissions import IsWalletOwner
from finance.serializers import (
    TransactionWriteOnlySerializer,
    TransactionReadOnlyModelSerializer,
    WalletModelSerializer
)
from django.db import (
    transaction,
    IntegrityError,
    OperationalError
)


class WalletCreation(
    mixins.CreateModelMixin,
    GenericViewSet
):
    serializer_class = WalletModelSerializer
    queryset = Wallet.objects.all()

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)


class TransactionViewSet(
    GenericViewSet
):
    serializer_class = TransactionWriteOnlySerializer
    queryset = Transaction.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        amount = convertor(data['amount'], 'int')
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

        if amount > origin_wallet._balance or \
                Transaction.is_daily_transfer_limit_exceeded(origin_wallet, amount):
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

    @action(
        detail=True,
        methods=['get']
    )
    def refund(self, request, pk='transaction_number'):
        origin_transaction = get_object_or_404(Transaction, transaction_number=pk)
        origin_wallet = origin_transaction.origin
        destination_wallet = origin_transaction.destination
        amount = convertor(origin_transaction.amount, 'int')
        if origin_transaction.status == TransactionStatusChoice.COMPLETE and \
                not hasattr(origin_transaction, 'refund_transactions'):
            with transaction.atomic():
                try:
                    refund_transaction = Transaction.objects.create(
                        origin=origin_wallet,
                        destination=destination_wallet,
                        _amount=amount,
                        status=TransactionStatusChoice.PENDING,
                        transaction_type=TransactionTypeChoice.REFUNDED,
                        original_transaction=origin_transaction
                    )
                except (IntegrityError, OperationalError):
                    # Transaction creation failed due to concurrent transaction
                    raise IntegrityError("Concurrent transaction, please try again.")

                origin_wallet._balance = F('_balance') + amount
                destination_wallet._balance = F('_balance') - amount
                origin_wallet.save()
                destination_wallet.save()
                refund_transaction.status = TransactionStatusChoice.COMPLETE
                refund_transaction.save()
                refund_transaction.refresh_from_db()
                return Response(
                    TransactionReadOnlyModelSerializer(refund_transaction).data,
                    status=status.HTTP_200_OK
                )
        else:
            return Response(
                MessageText.TransactionIsNotRefunded,
                status=status.HTTP_400_BAD_REQUEST
            )


class TransactionHistoryListAPIView(
    mixins.ListModelMixin,
    GenericViewSet
):
    permission_classes = [IsWalletOwner]
    serializer_class = TransactionReadOnlyModelSerializer
    pagination_class = CustomPaginator

    def get_serializer_context(self, *args, **kwargs):
        context = super().get_serializer_context()
        context['wallet_number'] = self.kwargs['wallet_number']
        return context

    def get_queryset(self):
        queryset = Transaction.objects.filter(Q(origin___wallet_number=self.kwargs.get('wallet_number')) |
                                              Q(destination___wallet_number=self.kwargs.get('wallet_number'))
                                              )
        return queryset
