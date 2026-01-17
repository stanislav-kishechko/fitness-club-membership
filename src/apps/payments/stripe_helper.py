import stripe
from django.conf import  settings
from .models import StripeCustomer, Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

def get_or_create_stripe_customer(user):
    customer_mapping = StripeCustomer.objects.filter(user=user).first()

    if customer_mapping:
        return customer_mapping.stripe_customer_id

    stripe_customer = stripe.Customer.create(
        email=user.email,
        metadata={"user_id": user.id}
    )

    StripeCustomer.objects.create(
        user=user,
        stripe_customer_id=stripe_customer.id,
    )

    return stripe_customer.id

def create_checkout_session(
        payment: Payment,
        success_url: str,
        cancel_url: str):
    customer_id = get_or_create_stripe_customer(payment.user)

    try:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "USD",
                    "product_data": {
                        "name": f"Fitness Club: {payment.get_type_display()}",
                        "description": f"Plan ID: {payment.membership_id}",
                    },
                    "unit_amount": int(payment.money_to_pay * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,

            metadata={
                "payment_id": payment.id,
                "user_id": payment.user.id,
            }
        )
        payment.session_id = session.id
        payment.session_url = session.url
        payment.save()

        return session

    except stripe.error.CardError as e:
        payment.status = Payment.StatusChoices.FAILED
        payment.error_message = f"Card Error: {e.user_message}"
        payment.save()
        raise e

    except stripe.error.StripeError as e:
        payment.status = Payment.StatusChoices.FAILED
        payment.error_message = "Stripe service error. Try again later."
        payment.save()
        raise e

    # noinspection PyBroadException
    except Exception as e:
        payment.status = Payment.StatusChoices.FAILED
        payment.error_message = f"Internal error: {str(e)}"
        payment.save()
        raise e
