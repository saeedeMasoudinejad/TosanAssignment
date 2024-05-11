from django.contrib import admin

from finance.models import Wallet, Transaction

admin.site.register(Wallet)
admin.site.register(Transaction, )

# TODO: Handle refund with admin
