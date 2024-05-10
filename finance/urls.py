from django.urls import path, include

from rest_framework.routers import DefaultRouter

from finance.views import WalletCreation, TransactionViewSet

router = DefaultRouter()
# user routes


router.register(
    prefix="transaction",
    viewset=TransactionViewSet,
    basename="transaction"
)

urlpatterns = [
    path('create-wallet/', WalletCreation.as_view(
        {'post': 'create'}),
         name='wallet-creation'
         ),
    path('', include(router.urls)),

]
