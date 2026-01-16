from datetime import date, timedelta
from django.db import transaction

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.membership.models import Membership
from apps.membership.serializers import MembershipReadSerializer, MembershipCreateSerializer, FreezeSerializer
from apps.payments.models import Payment
from apps.plans.models import MembershipPlan


class MembershipViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Membership.objects.all()
        user = self.request.user

        if not user.is_staff:
            queryset = queryset.filter(member=user)
        else:
            # Адмін може фільтрувати по member_id
            member_id = self.request.query_params.get("member_id")
            if member_id:
                queryset = queryset.filter(member_id=member_id)

        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        auto_renew = self.request.query_params.get("auto_renew")
        if auto_renew is not None:
            queryset = queryset.filter(auto_renew=auto_renew.lower() == "true")

        from_date = self.request.query_params.get("from")
        to_date = self.request.query_params.get("to")
        if from_date:
            queryset = queryset.filter(start_date__gte=from_date)
        if to_date:
            queryset = queryset.filter(end_date__lte=to_date)

        return queryset

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return MembershipReadSerializer
        return MembershipCreateSerializer

    def perform_create(self, serializer):
        plan = serializer.validated_data["plan"]
        start_date = date.today()
        end_date = start_date + timedelta(days=plan.duration_days)

        with transaction.atomic():
            membership = serializer.save(
                member=self.request.user,
                start_date=start_date,
                end_date=end_date,
                price_at_purchase=plan.price,
                status=Membership.Status.ACTIVE
            )

            # Створюємо платіж (Payment) через модель іншої людини
            # Тут викликається логіка створення Stripe сесії
            Payment.objects.create(
                membership=membership,
                payment_type=Payment.Type.MEMBERSHIP_PURCHASE,
                money_to_pay=plan.price,
                status=Payment.Status.PENDING
            )

    @action(detail=True, methods=["post"])
    def freeze(self, request, pk=None):
        membership = self.get_object()
        if membership.status != Membership.Status.ACTIVE:
            return Response({"error": "Only an active subscription can be frozen."}, status=400)

        serializer = FreezeSerializer(data=request.data)
        if serializer.is_valid():
            membership.status = Membership.Status.FROZEN
            membership.frozen_from = serializer.validated_data['frozen_from']
            membership.frozen_to = serializer.validated_data['frozen_to']

            freeze_days = (membership.frozen_to - membership.frozen_from).days
            membership.end_date += timedelta(days=freeze_days)

            membership.save()
            return Response(MembershipReadSerializer(membership).data)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=["post"])
    def resume(self, request, pk=None):
        membership = self.get_object()
        if membership.status != Membership.Status.FROZEN:
            return Response({"error": "The subscription is not frozen."}, status=400)

        membership.status = Membership.Status.ACTIVE
        membership.frozen_from = None
        membership.frozen_to = None
        membership.save()
        return Response(MembershipReadSerializer(membership).data)

    @action(detail=True, methods=["post"])
    def upgrade(self, request, pk=None):
        membership = self.get_object()
        new_plan_id = request.query_params.get("plan_id")

        try:
            new_plan = MembershipPlan.objects.get(id=new_plan_id)
        except MembershipPlan.DoesNotExist:
            return Response({"error": "Plan not found."}, status=404)

        if new_plan.price <= membership.price_at_purchase:
            return Response({"error": "Upgrade is only possible to a more expensive plan."}, status=400)

        diff_price = new_plan.price - membership.price_at_purchase

        with transaction.atomic():
            membership.plan = new_plan
            membership.price_at_purchase = new_plan.price
            membership.end_date = membership.start_date + timedelta(days=new_plan.duration_days)
            membership.save()

            Payment.objects.create(
                membership=membership,
                payment_type=Payment.Type.UPGRADE_FEE,
                money_to_pay=diff_price,
                status=Payment.Status.PENDING
            )

        return Response(MembershipReadSerializer(membership).data)
