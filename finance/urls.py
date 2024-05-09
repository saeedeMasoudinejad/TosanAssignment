from django.urls import path
from finance.views import WalletCreation

urlpatterns = [
    path('create-wallet/', WalletCreation.as_view({'post': 'create'}), name='wallet-creation'),

]
