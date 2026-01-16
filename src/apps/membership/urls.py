from django.urls import path, include
from rest_framework import routers

from apps.membership.views import MembershipViewSet

router = routers.DefaultRouter()
router.register("memberships", MembershipViewSet, basename="membership")

urlpatterns = [
    path("", include(router.urls)),
]
