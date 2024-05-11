from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from user.views import (
    UserSignupView,
    ProfileViewSet
)

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('refresh_token/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileViewSet.as_view({'get': 'retrieve'}), name='profile')
]
