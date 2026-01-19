from rest_framework import serializers
from apps.payments.models import Payment
from apps.membership.models import MembershipPlan
from apps.plans.models import MembershipPlan


class PaymentCreateSerializer(serializers.ModelSerializer):
    membership = serializers.PrimaryKeyRelatedField(
        queryset=MembershipPlan.objects.all(),
        source='membership_id'
    )

    class Meta:
        model = Payment
        fields = ["membership"]

    def validate_membership_id(self, value):
        if not MembershipPlan.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Plan with id {value} does not exist.")

        return value


class PaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "money_to_pay",
            "status",
            "type",
            "created_at",
            "error_message"
        ]
