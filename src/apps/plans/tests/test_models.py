from django.test import TestCase
from django.db import IntegrityError
from apps.plans.models import MembershipPlan


class MembershipPlanModelTest(TestCase):
    def test_str_representation(self) -> None:
        plan = MembershipPlan.objects.create(
            name="Basic Plan",
            code="basic",
            duration_days=30,
            price=100,
            tier=MembershipPlan.Tier.BASIC,
        )

        self.assertEqual(str(plan), "Basic Plan (BASIC)")

    def test_ordering_by_price(self) -> None:
        MembershipPlan.objects.create(
            name="Expensive",
            code="expensive",
            duration_days=30,
            price=200,
            tier=MembershipPlan.Tier.PREMIUM,
        )
        MembershipPlan.objects.create(
            name="Cheap",
            code="cheap",
            duration_days=30,
            price=50,
            tier=MembershipPlan.Tier.BASIC,
        )

        plans = MembershipPlan.objects.all()
        self.assertEqual(plans[0].price, 50)

    def test_tier_choices(self) -> None:
        plan = MembershipPlan.objects.create(
            name="Standard Plan",
            code="standard",
            duration_days=30,
            price=100,
            tier=MembershipPlan.Tier.STANDARD,
        )

        self.assertEqual(plan.tier, "STANDARD")
        self.assertIn(plan.tier, MembershipPlan.Tier.values)

    def test_code_is_unique(self) -> None:
        MembershipPlan.objects.create(
            name="Basic Plan",
            code="basic",
            duration_days=30,
            price=100,
            tier=MembershipPlan.Tier.BASIC,
        )

        with self.assertRaises(IntegrityError):
            MembershipPlan.objects.create(
                name="Another Basic",
                code="basic",  # duplicate
                duration_days=60,
                price=200,
                tier=MembershipPlan.Tier.STANDARD,
            )

    def test_duration_days_must_be_positive(self) -> None:
        with self.assertRaises(IntegrityError):
            MembershipPlan.objects.create(
                name="Invalid Duration",
                code="invalid-duration",
                duration_days=0,
                price=100,
                tier=MembershipPlan.Tier.BASIC,
            )

    def test_price_must_be_positive(self) -> None:
        with self.assertRaises(IntegrityError):
            MembershipPlan.objects.create(
                name="Invalid Price",
                code="invalid-price",
                duration_days=30,
                price=0,
                tier=MembershipPlan.Tier.BASIC,
            )
