from django.urls import path
from .views import StripeCheckoutView

urlpatterns = [
    path("create-checkout-session/", StripeCheckoutView.as_view(), name="create-checkout-session"),
]

app_name = "payments"