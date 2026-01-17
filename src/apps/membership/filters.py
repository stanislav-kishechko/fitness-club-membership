from django_filters import rest_framework as filters

from .models import Membership


class MembershipFilter(filters.FilterSet):
    start_date = filters.DateFromToRangeFilter()
    end_date = filters.DateFromToRangeFilter()

    auto_renew = filters.BooleanFilter()

    status = filters.ChoiceFilter(choices=Membership.Status.choices)
    member_id = filters.NumberFilter(field_name="member_id")

    class Meta:
        model = Membership
        fields = ["status", "auto_renew", "member_id", "start_date", "end_date"]
