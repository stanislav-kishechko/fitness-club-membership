import stripe, json

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from .serializers import PaymentCreateSerializer
from .models import Payment
from .stripe_helper import create_checkout_session
from apps.plans.models import MembershipPlan

class StripeCheckoutView(APIView):
    permission_classes = [] #TODO: need to change to auth

    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)

        if serializer.is_valid():
            membership_id = serializer.data["membership_id"]
            plan = MembershipPlan.objects.filter(id=membership_id).first()

            if not plan:
                return Response({"error":"Plan not found"}, status=status.HTTP_404_NOT_FOUND)
            User = get_user_model() #TODO: need to del this in prod
            first_user = User.objects.first() #TODO: need to del this in prod
            payment = Payment.objects.create(
                user = first_user,#TODO:user=request.user
                membership_id=serializer.data["membership_id"],
                money_to_pay=plan.price, # тимчасово статична ціна
                type=Payment.TypeChoices.MEMBERSHIP_PURCHASE,
            )

            try:
                session = create_checkout_session(
                    payment=payment,
                    success_url="http://localhost:3000/payments/success",
                    cancel_url="http://localhost:3000/payments/cancel",
                )

                return Response({"checkout_url": session.url}, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def stripe_webhook(request):

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    event = None

    try:
        #тут має бути перевірка підпису від страйп
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )

    except ValueError:
        return HttpResponse(status=400)

    if event.type == "checkout.session.completed":
        session = event.data.object
        payment_id = session.get("metadata", {}).get("payment_id")

        if payment_id:
            payment = Payment.objects.filter(id=payment_id).first()
            if payment:
                payment.status = Payment.StatusChoices.PAID
                payment.save()
                print(f"Payment {payment_id} succeeded!")
    return HttpResponse(status=200)