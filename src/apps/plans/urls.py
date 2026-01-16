from rest_framework.routers import DefaultRouter

from .views import MembershipPlanViewSet

router = DefaultRouter()
router.register("plans", MembershipPlanViewSet, basename="plans")

urlpatterns = router.urls
