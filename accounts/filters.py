from django.db.models import Q
from django_filters import rest_framework as filters

from accounts.models import UserTbl


class UserTblFilter(filters.FilterSet):
    # UUID Fields
    public_id = filters.UUIDFilter(field_name="public_id")
    tenant = filters.UUIDFilter(field_name="tenant_id")
    approved_by = filters.UUIDFilter(field_name="approved_by_id")

    # Char Fields
    email = filters.CharFilter(
        field_name="email",
        lookup_expr="icontains"
    )

    mobile_country_code = filters.CharFilter(
        field_name="mobile_country_code",
        lookup_expr="icontains"
    )

    mobile_number = filters.CharFilter(
        field_name="mobile_number",
        lookup_expr="icontains"
    )

    referral_source = filters.CharFilter(
        field_name="referral_source",
        lookup_expr="icontains"
    )

    referral_code = filters.CharFilter(
        field_name="referral_code",
        lookup_expr="icontains"
    )

    rejection_reason = filters.CharFilter(
        field_name="rejection_reason",
        lookup_expr="icontains"
    )

    # ManyToMany Field
    role = filters.CharFilter(method="filter_role")

    # Boolean Fields
    is_candidate = filters.BooleanFilter()
    is_mentor = filters.BooleanFilter()
    is_active = filters.BooleanFilter()
    is_staff = filters.BooleanFilter()
    is_superuser = filters.BooleanFilter()

    # Choice Fields
    approval_status = filters.ChoiceFilter(
        choices=UserTbl.ApprovalStatus.choices
    )

    mfa_method = filters.ChoiceFilter(
        choices=UserTbl.MfaMethod.choices
    )

    # Integer Field
    failed_login_attempts = filters.NumberFilter()

    # DateTime Fields
    email_verified_at = filters.DateTimeFromToRangeFilter()
    mobile_verified_at = filters.DateTimeFromToRangeFilter()
    approved_at = filters.DateTimeFromToRangeFilter()
    locked_until = filters.DateTimeFromToRangeFilter()
    last_login = filters.DateTimeFromToRangeFilter()
    date_joined = filters.DateTimeFromToRangeFilter()
    updated_at = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = UserTbl
        fields = [
            "public_id",
            "tenant",
            "email",
            "mobile_country_code",
            "mobile_number",
            "role",
            "is_candidate",
            "is_mentor",
            "approval_status",
            "email_verified_at",
            "mobile_verified_at",
            "mfa_method",
            "approved_by",
            "approved_at",
            "rejection_reason",
            "is_active",
            "is_staff",
            "is_superuser",
            "failed_login_attempts",
            "locked_until",
            "last_login",
            "date_joined",
            "referral_source",
            "referral_code",
            "updated_at",
        ]

    def filter_role(self, queryset, name, value):
        """
        Search by Role ID, Code or Name.
        """
        return queryset.filter(
            Q(role__id__iexact=value) |
            Q(role__code__icontains=value) |
            Q(role__name__icontains=value)
        ).distinct()