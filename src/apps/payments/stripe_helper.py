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