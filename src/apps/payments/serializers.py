from rest_framework import serializers
from .models import Payment

class PaymentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ["membership_id"]

        def validate_membership_id(self, value):
            ...
