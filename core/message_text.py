from django.utils.translation import gettext_lazy as _


class MessageText:
    # ALl 400 Error
    WalletNumberIsNotBelong = _("This wallet does not belong to you")
    WalletNumberNotFound = _("Wallet with this number does not")
    DailyTransferLimitExceeded = _("Daily transfer limit exceed.")