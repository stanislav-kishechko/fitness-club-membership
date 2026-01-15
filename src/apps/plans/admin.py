from django.contrib import admin

from apps.plans.models import MembershipPlan


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "tier", "price", "duration_days")
    prepopulated_fields = {"code": ("name",)}
