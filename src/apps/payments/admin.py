from django.contrib import admin

from .models import Payment, StripeCustomer


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "money_to_pay",
        "status",
        "type",
        "created_at",
        )

    list_filter = ("status", "type", "created_at")

    search_fields = ("user__username", "session_id", "error_message")

    readonly_fields = ("created_at", "updated_at", "session_id", "session_url")

@admin.register(StripeCustomer)
class StripeCustomerAdmin(admin.ModelAdmin):
    list_display = ("user", "stripe_customer_id")
    search_fields = ("user__username", "stripe_customer_id")

