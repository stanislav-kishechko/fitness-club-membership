from django.db import models


class MembershipPlan(models.Model):
    class Tier(models.TextChoices):
        BASIC = "BASIC", "Basic"
        STANDARD = "STANDARD", "Standard"
        PREMIUM = "PREMIUM", "Premium"

    name: models.CharField = models.CharField(max_length=100)
    code: models.SlugField = models.SlugField(unique=True)
    duration_days: models.PositiveIntegerField = models.PositiveIntegerField()
    price: models.DecimalField = models.DecimalField(max_digits=8, decimal_places=2)
    tier: models.CharField = models.CharField(max_length=20, choices=Tier.choices)

    class Meta:
        ordering = ["price"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(duration_days__gt=0), #TODO was check=models
                name="duration_days_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(price__gt=0),  #TODO was check=models
                name="price_positive",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.tier})"
