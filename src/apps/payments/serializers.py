from rest_framework import serializers
from .models import Payment
from apps.plans.models import MembershipPlan


class PaymentCreateSerializer(serializers.ModelSerializer):
    membership_id = serializers.IntegerField(required=True)

    class Meta:
        model = Payment
        fields = ["membership_id"]

    def validate_membership_id(self, value):
        if not MembershipPlan.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Plan with id {value} does not exist.")

        return value
