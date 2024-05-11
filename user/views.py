from rest_framework import status, mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from user.serializers import UserSerializer, ProfileReadOnlySerializer


class UserSignupView(
    APIView
):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data
        )
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
                status=status.HTTP_201_CREATED)
        # TODO: Standardize the output format of all responses.
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ProfileViewSet(
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    serializer_class = ProfileReadOnlySerializer

    def get_object(self):
        return self.request.user
