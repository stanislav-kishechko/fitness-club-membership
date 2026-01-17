from rest_framework.viewsets import ModelViewSet

from apps.plans.models import MembershipPlan
from apps.plans.permissions import IsAuthenticatedStaff
from apps.plans.serializers import MembershipPlanSerializer


class MembershipPlanViewSet(ModelViewSet):
    queryset = MembershipPlan.objects.all()
    serializer_class = MembershipPlanSerializer
    permission_classes = (IsAuthenticatedStaff,)
    filterset_fields = ("tier",)
