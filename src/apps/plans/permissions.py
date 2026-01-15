from typing import Any, cast

from django.contrib.auth.models import AbstractUser
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request


class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request: Request, _view: Any) -> bool:
        if request.method in SAFE_METHODS:
            return True

        user = cast(AbstractUser, request.user)
        return bool(user.is_authenticated and user.is_staff)
