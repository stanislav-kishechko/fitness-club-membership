from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from serializers import PaymentCreateSerializer
from .models import Payment
from .stripe_helper import create_checkout_session

class StripeCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)

        if serializer.is_valid():
            payment = Payment.objects.create(
                user=request.user,
                membership_id=serializer.data["membership_id"],
                money_to_pay=50, # тимчасово статична ціна
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
