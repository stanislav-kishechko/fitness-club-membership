from datetime import date
from rest_framework import serializers

from apps.membership.models import Membership
from apps.plans.models import MembershipPlan


class MembershipPlanShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipPlan
        fields = ["id", "name", "tier", "price"]


class MembershipReadSerializer(serializers.ModelSerializer):
    plan = MembershipPlanShortSerializer(read_only=True)
    member = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Membership
        fields = [
            "id",
            "member",
            "plan",
            "start_date",
            "end_date",
            "status",
            "auto_renew",
            "price_at_purchase",
            "frozen_from",
            "frozen_to"
        ]


class MembershipCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ["id", "plan", "auto_renew"]

    def validate(self, attrs):
        user = self.context["request"].user
        active_exists = Membership.objects.filter(
            member=user,
            status__in=["ACTIVE", "FROZEN"]
        ).exists()

        if active_exists:
            raise serializers.ValidationError("You already have an active or frozen subscription.")
        return attrs


class FreezeSerializer(serializers.Serializer):
    frozen_from = serializers.DateField(required=True)
    frozen_to = serializers.DateField(required=True)

    def validate(self, data):
        if data["frozen_from"] >= data["frozen_to"]:
            raise serializers.ValidationError("The 'to' date must be after the 'from' date.")
        if data["frozen_from"] < date.today():
            raise serializers.ValidationError("You can't freeze the past.")
        return data
