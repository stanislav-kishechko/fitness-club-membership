import logging
from datetime import date, timedelta

import stripe
from decouple import config
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.membership.models import Membership
from apps.payments.models import Payment
from apps.payments.serializers import PaymentCreateSerializer, PaymentListSerializer
from apps.payments.signals import payment_successful_signal
from apps.payments.stripe_helper import create_checkout_session
from apps.plans.models import MembershipPlan

from .models import Payment
from .serializers import PaymentCreateSerializer
from .stripe_helper import create_checkout_session

logger = logging.getLogger(__name__)


def create_or_update_membership(payment):
    """
    Creates or updates a user membership record based on a successful payment.
    Calculates start and end dates based on the MembershipPlan duration.
    """
    try:
        plan = MembershipPlan.objects.get(id=payment.membership_id)
        today = date.today()
        end_date = today + timedelta(days=plan.duration_days)

        membership, created = Membership.objects.update_or_create(
            member=payment.user,
            defaults={
                'plan': plan,
                'start_date': today,
                'end_date': end_date,
                'status': Membership.Status.ACTIVE,
                'price_at_purchase': payment.money_to_pay
            }
        )
        logger.info(f"Membership for user {payment.user.id} updated successfully.")
        return membership
    except MembershipPlan.DoesNotExist:
        logger.error(f"MembershipPlan with ID {payment.membership_id} not found.")
        raise


class StripeCheckoutView(APIView):
    """
    View for making payment session Stripe
    Includes logic Upgrade payments
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        membership_id = serializer.validated_data["membership_id"]
        new_plan = MembershipPlan.objects.get(id=membership_id)
        user = request.user

        # Idempotency on Django side
        time_threshold = timezone.now() - timedelta(minutes=15)

        recent_payment = Payment.objects.filter(
            user=user,
            membership_id=membership_id,
            status=Payment.StatusChoices.PENDING,
            created_at__gte=time_threshold
        ).first()

        if recent_payment and recent_payment.session_url:
            logger.info(f"Returning existing session for payment {recent_payment.id}")
            return Response({"checkout_url": recent_payment.session_url}, status=status.HTTP_200_OK)

        # Current membership for upgrade
        current_membership = Membership.objects.filter(
            member=user,
            status=Membership.Status.ACTIVE,
        ).first()

        money_to_pay = new_plan.price
        payment_type = Payment.TypeChoices.MEMBERSHIP_PURCHASE

        # Calculating UpgradeFee
        if current_membership:

            if new_plan.price <= current_membership.plan.price:
                return Response(
                    {"error": "You can choose only higher price plan to upgrade."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            today = date.today()
            if current_membership.end_date > today:
                remaining_days = (current_membership.end_date - today).days

                price_per_day_old = current_membership.plan.price / current_membership.plan.duration_days
                credit = price_per_day_old * remaining_days
                money_to_pay = max(0, new_plan.price - credit)
                payment_type = Payment.TypeChoices.UPGRADE_FEE

        payment = Payment.objects.create(
            user=user,
            membership_id=membership_id,
            money_to_pay=money_to_pay,
            type=payment_type,
            status=Payment.StatusChoices.PENDING,
        )

        try:
            success_url = request.build_absolute_uri(reverse('payments:success')) + "?session_id={CHECKOUT_SESSION_ID}"
            cancel_url = request.build_absolute_uri(reverse('payments:cancel'))

            session = create_checkout_session(
                payment=payment,
                success_url=success_url,
                cancel_url=cancel_url,
            )

            return Response({"checkout_url": session.url}, status=status.HTTP_201_CREATED)

        except Exception as e:
            payment.status = Payment.StatusChoices.FAILED
            payment.error_message = str(e)
            payment.save()
            return Response({"error": "Failed to create Stripe session."}, status=status.HTTP_400_BAD_REQUEST)


class PaymentHistoryView(generics.ListAPIView):
    """
    Returns the payment history for the current authenticated user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentListSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')


def payment_success(request):
    session_id = request.GET.get('session_id')
    if session_id:
        return HttpResponse(f"Success! Session ID: {session_id}")
    return HttpResponse("Invalid URL: No session_id found", status=400)


def payment_cancel(request):
    return HttpResponse("Payment canceled!")


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, config("STRIPE_WEBHOOK_SECRET")
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        logger.warning(f"Invalid webhook signature: {str(e)}")
        return HttpResponse(status=400)

    stripe_obj = event.data.object
    metadata = stripe_obj.get("metadata", {})
    payment_id = metadata.get("payment_id")

    if event.type == "checkout.session.completed":
        if payment_id:
            payment = Payment.objects.filter(id=payment_id).first()
            if payment and payment.status == Payment.StatusChoices.PENDING:
                payment.status = Payment.StatusChoices.PAID
                payment.save()
                create_or_update_membership(payment)
                logger.info(f"Payment {payment_id} marked as PAID.")
                payment_successful_signal.send(
                    sender=Payment,
                    instance=payment
                )

    elif event.type == "payment_intent.payment_failed":
        if payment_id:
            payment = Payment.objects.filter(id=payment_id).first()
            if payment:
                error_msg = stripe_obj.get("last_payment_error", {}).get("message", "Unknown error")
                payment.status = Payment.StatusChoices.FAILED
                payment.error_message = error_msg
                payment.save()
                logger.error(f"Payment {payment_id} failed: {error_msg}")

    return HttpResponse(status=200)
