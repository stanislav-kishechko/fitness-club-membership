from django.db import models
from django.conf import settings

from apps.plans.models import MembershipPlan


class Membership(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        EXPIRED = "EXPIRED", "Expired"
        FROZEN = "FROZEN", "Frozen"

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    plan = models.ForeignKey(
        MembershipPlan,
        on_delete=models.PROTECT,
        related_name="user_memberships"
    )

    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    auto_renew = models.BooleanField(default=False)

    price_at_purchase = models.DecimalField(max_digits=8, decimal_places=2)

    frozen_from = models.DateField(null=True, blank=True)
    frozen_to = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Membership #{self.id}: {self.member} - {self.plan.name}"
