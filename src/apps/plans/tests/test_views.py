from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.plans.models import MembershipPlan


class MembershipPlanViewSetTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="password123",
            is_staff=False,
        )

        self.staff_user = get_user_model().objects.create_user(
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

    def test_list_plans_anonymous_unauthorized(self):
        response = self.client.get(reverse("plans:plans-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_plans_non_staff_forbidden(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("plans:plans-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_plans_staff_allowed(self):
        self.client.force_authenticate(self.staff_user)
        response = self.client.get(reverse("plans:plans-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_plan_anonymous_unauthorized(self):
        response = self.client.get(reverse("plans:plans-detail", args=[self.plan.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_plan_non_staff_forbidden(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("plans:plans-detail", args=[self.plan.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_plan_staff_allowed(self):
        self.client.force_authenticate(self.staff_user)
        response = self.client.get(reverse("plans:plans-detail", args=[self.plan.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_plan_anonymous_unauthorized(self):
        payload = {
            "name": "Premium",
            "code": "premium",
            "duration_days": 90,
            "price": 300,
            "tier": MembershipPlan.Tier.PREMIUM,
        }

        response = self.client.post(reverse("plans:plans-list"), payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_plan_non_staff_forbidden(self):
        self.client.force_authenticate(self.user)

        payload = {
            "name": "Premium",
            "code": "premium",
            "duration_days": 90,
            "price": 300,
            "tier": MembershipPlan.Tier.PREMIUM,
        }

        response = self.client.post(reverse("plans:plans-list"), payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_plan_staff_allowed(self):
        self.client.force_authenticate(self.staff_user)

        payload = {
            "name": "Premium",
            "code": "premium",
            "duration_days": 90,
            "price": 300,
            "tier": MembershipPlan.Tier.PREMIUM,
        }

        response = self.client.post(reverse("plans:plans-list"), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(MembershipPlan.objects.filter(code="premium").exists())

    def test_update_plan_non_staff_forbidden(self):
        self.client.force_authenticate(self.user)

        response = self.client.patch(
            reverse("plans:plans-detail", args=[self.plan.id]),
            {"price": 150},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_plan_staff_allowed(self):
        self.client.force_authenticate(self.staff_user)

        response = self.client.patch(
            reverse("plans:plans-detail", args=[self.plan.id]),
            {"price": 150},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.plan.refresh_from_db()
        self.assertEqual(self.plan.price, 150)

    def test_delete_plan_non_staff_forbidden(self):
        self.client.force_authenticate(self.user)

        response = self.client.delete(reverse("plans:plans-detail", args=[self.plan.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_plan_staff_allowed(self):
        self.client.force_authenticate(self.staff_user)

        response = self.client.delete(reverse("plans:plans-detail", args=[self.plan.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(MembershipPlan.objects.filter(id=self.plan.id).exists())
