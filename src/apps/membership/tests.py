from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.membership.models import Membership
from apps.plans.models import MembershipPlan
from apps.payments.models import Payment


User = get_user_model()


class MembershipTestSuite(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="testuser@test", password="password123")
        self.admin = User.objects.create_superuser(email="admin@admin", password="adminpassword")

        self.basic_plan = MembershipPlan.objects.create(
            name="Basic", code=1, tier=1, price=100.00, duration_days=30
        )
        self.gold_plan = MembershipPlan.objects.create(
            name="Gold", code=2, tier=2, price=250.00, duration_days=90
        )

        self.list_url = reverse("membership:membership-list")

    def test_unauthenticated_access(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_queryset_filtering_for_regular_user(self):
        Membership.objects.all().delete()
        Membership.objects.create(
            member=self.admin, plan=self.basic_plan,
            start_date=date.today(), end_date=date.today() + timedelta(days=30),
            price_at_purchase=self.basic_plan.price
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)

        data = response.data.get("results", response.data)
        self.assertEqual(len(data), 0)

    def test_create_membership_success(self):
        self.client.force_authenticate(user=self.user)
        data = {"plan": self.basic_plan.id, "auto_renew": True}
        response = self.client.post(self.list_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data, "Response data should contain 'id'")
        membership_id = response.data["id"]
        self.assertEqual(Membership.objects.filter(member=self.user).count(), 1)

        self.assertTrue(
            Payment.objects.filter(membership_id=membership_id).exists(),
            f"Payment for membership {membership_id} was not created"
        )

    def test_validate_active_subscription_exists(self):
        Membership.objects.create(
            member=self.user, plan=self.basic_plan,
            start_date=date.today(), end_date=date.today() + timedelta(days=30),
            price_at_purchase=self.basic_plan.price, status=Membership.Status.ACTIVE
        )
        self.client.force_authenticate(user=self.user)
        data = {"plan": self.gold_plan.id}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_freeze_action_logic(self):
        m = Membership.objects.create(
            member=self.user, plan=self.basic_plan,
            start_date=date.today(), end_date=date.today() + timedelta(days=30),
            price_at_purchase=self.basic_plan.price, status=Membership.Status.ACTIVE
        )
        self.client.force_authenticate(user=self.user)
        url = reverse("membership:membership-freeze", args=[m.id])

        freeze_from = date.today() + timedelta(days=1)
        freeze_to = date.today() + timedelta(days=11)

        data = {
            "frozen_from": str(freeze_from),
            "frozen_to": str(freeze_to)
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        m.refresh_from_db()
        self.assertEqual(m.status, Membership.Status.FROZEN)
        self.assertEqual(response.data["status"], "FROZEN")

    def test_resume_action_logic(self):
        m = Membership.objects.create(
            member=self.user, plan=self.basic_plan,
            start_date=date.today(), end_date=date.today() + timedelta(days=30),
            price_at_purchase=self.basic_plan.price, status=Membership.Status.FROZEN,
            frozen_from=date.today(), frozen_to=date.today() + timedelta(days=5)
        )
        self.client.force_authenticate(user=self.user)
        url = reverse("membership:membership-resume", args=[m.id])

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        m.refresh_from_db()
        self.assertEqual(m.status, Membership.Status.ACTIVE)
        self.assertIsNone(m.frozen_from)

    def test_upgrade_action_logic(self):
        m = Membership.objects.create(
            member=self.user, plan=self.basic_plan,
            start_date=date.today(), end_date=date.today() + timedelta(days=30),
            price_at_purchase=100.00, status=Membership.Status.ACTIVE
        )
        self.client.force_authenticate(user=self.user)
        url = reverse("membership:membership-upgrade", args=[m.id]) + f"?plan_id={self.gold_plan.id}"

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        m.refresh_from_db()
        self.assertEqual(m.plan, self.gold_plan)
        self.assertEqual(float(m.price_at_purchase), 250.00)

    def test_membership_filters(self):
        Membership.objects.all().delete()

        m1 = Membership.objects.create(
            member=self.user, plan=self.basic_plan,
            start_date=date.today(), end_date=date.today() + timedelta(days=30),
            price_at_purchase=100.00, status=Membership.Status.ACTIVE,
            auto_renew=True
        )
        m2 = Membership.objects.create(
            member=self.user, plan=self.basic_plan,
            start_date=date.today() - timedelta(days=40),
            end_date=date.today() - timedelta(days=10),
            price_at_purchase=100.00, status=Membership.Status.EXPIRED,
            auto_renew=False
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.list_url, {"status": "ACTIVE"})
        data = response.data.get("results", response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], m1.id)

        response = self.client.get(self.list_url, {"status": "ACTIVE", "auto_renew": "false"})
        data = response.data.get("results", response.data)

        self.assertEqual(len(data), 0)

    def test_membership_str_method(self):
        m = Membership.objects.create(
            member=self.user, plan=self.basic_plan,
            start_date=date.today(), end_date=date.today() + timedelta(days=30),
            price_at_purchase=100.00
        )
        expected_str = f"Membership #{m.id}: {self.user} - {self.basic_plan.name}"
        self.assertEqual(str(m), expected_str)
