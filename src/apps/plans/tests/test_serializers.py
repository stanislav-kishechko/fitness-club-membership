from decimal import Decimal

from django.test import TestCase

from apps.plans.models import MembershipPlan
from apps.plans.serializers import MembershipPlanSerializer


class MembershipPlanSerializerTestCase(TestCase):
    def test_valid_data(self):
        data = {
            "name": "Basic Plan",
            "code": "basic",
            "duration_days": 30,
            "price": Decimal("99.99"),
            "tier": MembershipPlan.Tier.BASIC,
        }

        serializer = MembershipPlanSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_duration_days_must_be_positive(self):
        data = {
            "name": "Invalid Plan",
            "code": "invalid-duration",
            "duration_days": 0,
            "price": Decimal("99.99"),
            "tier": MembershipPlan.Tier.BASIC,
        }

        serializer = MembershipPlanSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("duration_days", serializer.errors)

    def test_price_must_be_positive(self):
        data = {
            "name": "Free Plan",
            "code": "free",
            "duration_days": 30,
            "price": Decimal("0.00"),
            "tier": MembershipPlan.Tier.BASIC,
        }

        serializer = MembershipPlanSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)

    def test_invalid_tier(self):
        data = {
            "name": "Wrong Tier",
            "code": "wrong-tier",
            "duration_days": 30,
            "price": Decimal("99.99"),
            "tier": "GOLD",
        }

        serializer = MembershipPlanSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("tier", serializer.errors)

    def test_code_must_be_unique(self):
        MembershipPlan.objects.create(
            name="Basic Plan",
            code="basic",
            duration_days=30,
            price=Decimal("99.99"),
            tier=MembershipPlan.Tier.BASIC,
        )

        data = {
            "name": "Another Plan",
            "code": "basic",  # duplicate
            "duration_days": 60,
            "price": Decimal("199.99"),
            "tier": MembershipPlan.Tier.STANDARD,
        }

        serializer = MembershipPlanSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("code", serializer.errors)

    def test_id_is_read_only(self):
        data = {
            "id": 999,
            "name": "Basic Plan",
            "code": "basic",
            "duration_days": 30,
            "price": Decimal("99.99"),
            "tier": MembershipPlan.Tier.BASIC,
        }

        serializer = MembershipPlanSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertNotIn("id", serializer.validated_data)
