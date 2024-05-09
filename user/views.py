from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from user.serializers import UserSerializer


class UserSignupView(
    APIView
):
    permission_classes = [AllowAny]

    def post(
            self,
            request
    ):
        serializer = UserSerializer(
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
