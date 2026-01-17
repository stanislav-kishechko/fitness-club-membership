from django.urls import path
from .views import (
    StripeCheckoutView,
    stripe_webhook,
    payment_cancel,
    payment_success,
)

urlpatterns = [
    path("create-checkout-session/", StripeCheckoutView.as_view(), name="create-checkout-session"),
    path("webhook/", stripe_webhook, name="stripe-webhook"),
    path("success/", payment_success, name="success"),
    path("cancel/", payment_cancel, name="cancel"),
]

app_name = "payments"