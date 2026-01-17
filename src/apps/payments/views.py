import stripe

from datetime import date

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework import status
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


from .serializers import PaymentCreateSerializer
from .models import Payment
from .stripe_helper import create_checkout_session
from apps.plans.models import MembershipPlan
from apps.membership.models import Membership
from decouple import config

class StripeCheckoutView(APIView):
    """
    View for making payment session Srtipe
    Includes logic Upgrage payments
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        membership_id = serializer.validated_data["membership_id"]
        new_plan = MembershipPlan.objects.get(id=membership_id)
        user = request.user

        #Current membership for upgrade
        current_membership = Membership.objects.filter(
            member=user,
            status=Membership.Status.ACTIVE,
        ).first()

        money_to_pay = new_plan.price
        payment_type = Payment.TypeChoices.MEMBERSHIP_PURCHASE

        #Calculating UpgradeFee
        if current_membership:

            if new_plan.tier <= current_membership.plan.tier and new_plan.price <= current_membership.plan.price:
                return Response(
                    {"error": "You can choose only higher tier plan to upgrade."},
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


def payment_success(request):
    """
        Handles successful payment redirect.
        Retrieves session_id from URL to confirm specific transaction.
    """
    session_id = request.GET.get('session_id')
    if session_id:
        return HttpResponse(
            f"Success! Your payment is processed. Session ID: {session_id}. "
            f"Your membership is being activated."
        )
    return HttpResponse("Payment succeeded! Your membership is being activated.")

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

    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event.type == "checkout.session.completed":
        session = event.data.object
        payment_id = session.get("metadata", {}).get("payment_id")

        if payment_id:
            payment = Payment.objects.filter(id=payment_id).first()
            if payment and payment.status != Payment.StatusChoices.PAID:
                payment.status = Payment.StatusChoices.PAID
                payment.save()
                print(f"Payment {payment_id} succeeded!")
                #create_or_update_membership(payment)

    return HttpResponse(status=200)