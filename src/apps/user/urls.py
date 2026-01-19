from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from apps.user.views import CreateUserView, ManageUserView

app_name = "user"

urlpatterns = [
    path("user/", CreateUserView.as_view(), name="create"),
    path("user/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("user/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("user/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("user/me/", ManageUserView.as_view(), name="manage"),
]
