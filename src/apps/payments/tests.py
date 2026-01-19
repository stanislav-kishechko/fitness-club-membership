import pytest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.payments.models import Payment
from apps.membership.models import Membership
from apps.plans.models import MembershipPlan
from apps.payments.views import create_or_update_membership

User = get_user_model()


@pytest.mark.django_db
class TestPaymentFullCoverage:

    @pytest.fixture
    def setup_data(self):
        user = User.objects.create_user(email="test@fitness.com", password="password")
        plan = MembershipPlan.objects.create(
            id=1, name="Standard", duration_days=30, price=100.00
        )
        client = APIClient()
        client.force_authenticate(user=user)
        return user, plan, client

    def test_create_membership_success(self, setup_data):
        user, plan, _ = setup_data
        payment = Payment.objects.create(
            user=user, membership_id=plan.id, money_to_pay=100,
            status=Payment.StatusChoices.PENDING, type=Payment.TypeChoices.MEMBERSHIP_PURCHASE
        )
        create_or_update_membership(payment)
        membership = Membership.objects.get(member=user)
        assert membership.status == Membership.Status.ACTIVE
        assert membership.end_date == date.today() + timedelta(days=30)

    def test_create_membership_plan_not_found(self, setup_data, caplog):
        user, _, _ = setup_data
        payment = Payment.objects.create(
            user=user, membership_id=999, money_to_pay=100, status=Payment.StatusChoices.PAID
        )
        create_or_update_membership(payment)
        assert "Plan 999 not found" in caplog.text

    @patch("stripe.Webhook.construct_event")
    def test_webhook_success(self, mock_webhook, client, setup_data):
        user, plan, _ = setup_data
        payment = Payment.objects.create(
            user=user, membership_id=plan.id, money_to_pay=100, status=Payment.StatusChoices.PENDING
        )
        mock_event = MagicMock()
        mock_event.type = "checkout.session.completed"
        mock_event.data.object = {"metadata": {"payment_id": str(payment.id)}}
        mock_webhook.return_value = mock_event

        url = reverse("payments:stripe-webhook")
        response = client.post(url, data={}, content_type="application/json")
        payment.refresh_from_db()
        assert response.status_code == 200
        assert payment.status == Payment.StatusChoices.PAID

    @patch("stripe.Webhook.construct_event")
    def test_webhook_payment_failed(self, mock_webhook, client, setup_data):
        user, plan, _ = setup_data
        payment = Payment.objects.create(
            user=user, membership_id=plan.id, money_to_pay=100, status=Payment.StatusChoices.PENDING
        )
        mock_event = MagicMock()
        mock_event.type = "payment_intent.payment_failed"
        mock_event.data.object = {
            "metadata": {"payment_id": str(payment.id)},
            "last_payment_error": {"message": "Insufficient funds"}
        }
        mock_webhook.return_value = mock_event

        url = reverse("payments:stripe-webhook")
        response = client.post(url, data={}, content_type="application/json")
        payment.refresh_from_db()
        assert payment.status == Payment.StatusChoices.FAILED
        assert payment.error_message == "Insufficient funds"

    @patch("stripe.Webhook.construct_event")
    def test_webhook_invalid_signature(self, mock_webhook, client):
        import stripe
        mock_webhook.side_effect = stripe.error.SignatureVerificationError("Invalid sig", "header")
        url = reverse("payments:stripe-webhook")
        response = client.post(url, data={}, content_type="application/json")
        assert response.status_code == 400

    def test_payment_history_view(self, setup_data):
        user, plan, client = setup_data
        Payment.objects.create(
            user=user, membership_id=plan.id, money_to_pay=50,
            type=Payment.TypeChoices.UPGRADE_FEE, status=Payment.StatusChoices.PAID
        )
        url = reverse("payments:history")
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_payment_success_view(self, client):
        url = reverse("payments:success") + "?session_id=test_id"
        response = client.get(url)
        assert response.status_code == 200
        assert b"Success!" in response.content

    def test_payment_success_no_id(self, client):
        url = reverse("payments:success")
        response = client.get(url)
        assert response.status_code == 400

    def test_payment_cancel_view(self, client):
        url = reverse("payments:cancel")
        response = client.get(url)
        assert response.status_code == 200
        assert b"canceled" in response.content