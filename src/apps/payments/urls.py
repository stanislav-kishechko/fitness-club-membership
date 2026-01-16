from django.urls import path
from .views import StripeCheckoutView, stripe_webhook

urlpatterns = [
    path("create-checkout-session/", StripeCheckoutView.as_view(), name="create-checkout-session"),
    path("webhook/", stripe_webhook, name="stripe-webhook"),
]

app_name = "payments"