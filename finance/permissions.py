from rest_framework.permissions import BasePermission

from finance.models import Wallet


class IsWalletOwner(BasePermission):
    @staticmethod
    def _has_permission(request, view):
        if Wallet.objects.get(_wallet_number=view.kwargs['wallet_number']).owner == request.user:
            return True
        return False

    def has_permission(self, request, view):
        return self._has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return self._has_permission(request, view)

