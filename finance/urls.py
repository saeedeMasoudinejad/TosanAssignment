from django.urls import path, include

from rest_framework.routers import DefaultRouter

from finance.views import (
    WalletCreation,
    TransactionViewSet,
    TransactionHistoryListAPIView
)

router = DefaultRouter()

router.register(
    prefix="transaction",
    viewset=TransactionViewSet,
    basename="transaction"
)

urlpatterns = [
    path('create-wallet/',
         WalletCreation.as_view(
             {'post': 'create'}
         ),
         name='wallet-creation'
         ),
    path('<int:wallet_number>/history',
         TransactionHistoryListAPIView.as_view(
             {'get': 'list'}
         ),
         name='transaction-history'),
    path('', include(router.urls)),

]
