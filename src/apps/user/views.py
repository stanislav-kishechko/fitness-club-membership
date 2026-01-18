from typing import Any

from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.settings import api_settings
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.user.serializers import AuthTokenSerializer, UserSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class CreateTokenView(ObtainAuthToken):
    renderer_classes: Any = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self) -> Any:
        return self.request.user
