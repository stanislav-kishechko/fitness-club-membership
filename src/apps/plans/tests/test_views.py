from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.plans.models import MembershipPlan

PLANS_URL = "/api/v1/plans/"


class MembershipPlanViewSetTest(APITestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="user@test.com",
            password="password123",
            is_staff=False,
        )

        self.staff_user = get_user_model().objects.create_user(
            username="staffuser",
            email="staff@test.com",
            password="password123",
            is_staff=True,
        )

        self.plan = MembershipPlan.objects.create(
            name="Basic",
            code="basic",
            duration_days=30,
            price=100,
            tier=MembershipPlan.Tier.BASIC,
        )

    def test_list_plans_anonymous_forbidden(self):
        response = self.client.get(PLANS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_plans_non_staff_forbidden(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(PLANS_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_plans_staff_allowed(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(PLANS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_plan_staff_allowed(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(f"{PLANS_URL}{self.plan.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_plan_non_staff_forbidden(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"{PLANS_URL}{self.plan.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_plan_anonymous_forbidden(self):
        response = self.client.get(f"{PLANS_URL}{self.plan.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_plan_staff_allowed(self):
        self.client.force_authenticate(user=self.staff_user)

        payload = {
            "name": "Premium",
            "code": "premium",
            "duration_days": 90,
            "price": 300,
            "tier": MembershipPlan.Tier.PREMIUM,
        }

        response = self.client.post(PLANS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(MembershipPlan.objects.filter(code="premium").exists())

    def test_create_plan_non_staff_forbidden(self):
        self.client.force_authenticate(user=self.user)

        payload = {
            "name": "Premium",
            "code": "premium",
            "duration_days": 90,
            "price": 300,
            "tier": MembershipPlan.Tier.PREMIUM,
        }

        response = self.client.post(PLANS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_plan_staff_allowed(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.patch(
            f"{PLANS_URL}{self.plan.id}/",
            {"price": 150},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.plan.refresh_from_db()
        self.assertEqual(self.plan.price, 150)

    def test_delete_plan_staff_allowed(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.delete(f"{PLANS_URL}{self.plan.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(MembershipPlan.objects.filter(id=self.plan.id).exists())
