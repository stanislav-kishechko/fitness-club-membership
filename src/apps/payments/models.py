from django.db import models
from django.conf import settings

class Payment(models.Model):
    """
    Model for payments and tracking errors
    """
    class StatusChoices(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"
        REJECTED = "REJECTED", "Rejected"
        EXPIRED = "EXPIRED", "Expired"

    class TypeChoices(models.TextChoices):
        MEMBERSHIP_PURCHASE = "MEMBERSHIP_PURCHASE", "Membership Purchase"
        UPGRADE_FEE = "UPGRADE_FEE", "Upgrade Fee"

    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    type = models.CharField(
        max_length=10,
        choices=TypeChoices.choices,
    )

    membership_id = models.PositiveIntegerField()

    money_to_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Money from membership to payment",
    )

    #Field for tracking errors
    error_message = models.TextField(
        blank=True,
        null=True,
        help_text="Error message from Stripe",
    )

    session_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
    )

    session_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment {self.id} ({self.status} - {self.money_to_pay} USD)"

    """
    Model for tracking members billing profiles
    """
    class StripeCustomer(models.Model):
        user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
        stripe_customer_id = models.CharField(
            max_length=255,
            unique=True,
        )

        def __str__(self):
            return f"Stripe Customer ID: {self.stripe_customer_id}"

