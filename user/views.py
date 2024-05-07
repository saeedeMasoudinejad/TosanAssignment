from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from user.serializers import UserSerializer


class UserSignupView(
    APIView
):
    permission_classes = [AllowAny]

    # NOTE:swagger don't detect the request parameters, so It's required to be defined manually.
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format='password'),
            }
        )
    )
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
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
                status=status.HTTP_201_CREATED)
        # TODO: Standardize the output format of all responses.
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
