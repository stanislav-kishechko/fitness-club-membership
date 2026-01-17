from rest_framework import serializers

from apps.plans.models import MembershipPlan


class MembershipPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipPlan
        fields = (
            "id",
            "name",
            "code",
            "duration_days",
            "price",
            "tier",
        )
        read_only_fields = ("id",)

    def validate_duration_days(self, value: int) -> int:
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value
