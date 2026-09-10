from rest_framework import serializers
from .models import *
from django.core.exceptions import ValidationError


class AuditEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditEvent
        fields = "__all__"
        read_only_fields = (
            "id",
            "occurred_at",
            "correlation_id",
        )

class CalculatedFieldOverrideSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculatedFieldOverride
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

class CalculatedFieldValueHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculatedFieldValueHistory
        fields = "__all__"
        read_only_fields = (
            "created_at",
        )

class CalculationRuleSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculationRuleSet
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class CalculationRuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = CalculationRule
        fields = "__all__"
        read_only_fields = (
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        instance = self.instance

        calculation_field_code = attrs.get("calculation_field_code", getattr(instance, "calculation_field_code", None) if instance else None)
        tenant = attrs.get("tenant", getattr(instance, "tenant", None) if instance else None)
        scopes = attrs.get("scope", None)

        concluded_qualion_level = attrs.get("concluded_qualion_level", getattr(instance, "concluded_qualion_level", None) if instance else None)
        concluded_deployability_status = attrs.get("concluded_deployability_status", getattr(instance, "concluded_deployability_status", "") if instance else "")
        concluded_classification = attrs.get("concluded_classification", getattr(instance, "concluded_classification", "") if instance else "")

        if instance and scopes is None:
            scopes = list(instance.scope.all())

        if scopes is None:
            scopes = []

        requested_scope_ids = {scope.pk for scope in scopes}

        if calculation_field_code == CalculatedFieldCode.QUALION_LEVEL:
            if not concluded_qualion_level:
                raise serializers.ValidationError({"concluded_qualion_level": "This field is required for QUALION_LEVEL rules."})

            duplicate_queryset = CalculationRule.objects.filter(tenant=tenant, calculation_field_code=CalculatedFieldCode.QUALION_LEVEL, concluded_qualion_level=concluded_qualion_level)

            if concluded_deployability_status:
                raise serializers.ValidationError({"concluded_deployability_status": "Not applicable for QUALION_LEVEL rules."})

            if concluded_classification:
                raise serializers.ValidationError({"concluded_classification": "Not applicable for QUALION_LEVEL rules."})

        elif calculation_field_code == CalculatedFieldCode.DEPLOYABILITY_FLAG:
            if not concluded_deployability_status:
                raise serializers.ValidationError({"concluded_deployability_status": "This field is required for DEPLOYABILITY_FLAG rules."})

            duplicate_queryset = CalculationRule.objects.filter(tenant=tenant, calculation_field_code=CalculatedFieldCode.DEPLOYABILITY_FLAG, concluded_deployability_status=concluded_deployability_status)

            if concluded_qualion_level:
                raise serializers.ValidationError({"concluded_qualion_level": "Not applicable for DEPLOYABILITY_FLAG rules."})

            if concluded_classification:
                raise serializers.ValidationError({"concluded_classification": "Not applicable for DEPLOYABILITY_FLAG rules."})

        elif calculation_field_code == CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION:
            if not concluded_classification:
                raise serializers.ValidationError({"concluded_classification": "This field is required for CANDIDATE_MENTOR_CLASSIFICATION rules."})

            duplicate_queryset = CalculationRule.objects.filter(tenant=tenant, calculation_field_code=CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION, concluded_classification=concluded_classification)

            if concluded_qualion_level:
                raise serializers.ValidationError({"concluded_qualion_level": "Not applicable for CANDIDATE_MENTOR_CLASSIFICATION rules."})

            if concluded_deployability_status:
                raise serializers.ValidationError({"concluded_deployability_status": "Not applicable for CANDIDATE_MENTOR_CLASSIFICATION rules."})

        else:
            raise serializers.ValidationError({"calculation_field_code": "Invalid calculation field code."})

        if instance:
            duplicate_queryset = duplicate_queryset.exclude(pk=instance.pk)

        for existing_rule in duplicate_queryset.prefetch_related("scope"):
            existing_scope_ids = set(existing_rule.scope.values_list("pk", flat=True))

            if not requested_scope_ids and not existing_scope_ids:
                raise serializers.ValidationError({"scope": "A tenant-wide rule already exists with the same concluded value."})

            duplicate_scope_ids = requested_scope_ids.intersection(existing_scope_ids)

            if duplicate_scope_ids:
                raise serializers.ValidationError({"scope": f"A rule already exists for scope ID(s) {sorted(duplicate_scope_ids)} with the same concluded value."})

        min_calendar_experience_months = attrs.get("min_calendar_experience_months", getattr(instance, "min_calendar_experience_months", None) if instance else None)
        max_calendar_experience_months = attrs.get("max_calendar_experience_months", getattr(instance, "max_calendar_experience_months", None) if instance else None)

        if min_calendar_experience_months is not None and max_calendar_experience_months is not None and min_calendar_experience_months > max_calendar_experience_months:
            raise serializers.ValidationError({"max_calendar_experience_months": "Maximum value must be greater than or equal to minimum value."})

        min_verified_field_days = attrs.get("min_verified_field_days", getattr(instance, "min_verified_field_days", None) if instance else None)
        max_verified_field_days = attrs.get("max_verified_field_days", getattr(instance, "max_verified_field_days", None) if instance else None)

        if min_verified_field_days is not None and max_verified_field_days is not None and min_verified_field_days > max_verified_field_days:
            raise serializers.ValidationError({"max_verified_field_days": "Maximum value must be greater than or equal to minimum value."})

        min_verified_project_count = attrs.get("min_verified_project_count", getattr(instance, "min_verified_project_count", None) if instance else None)
        max_verified_project_count = attrs.get("max_verified_project_count", getattr(instance, "max_verified_project_count", None) if instance else None)

        if min_verified_project_count is not None and max_verified_project_count is not None and min_verified_project_count > max_verified_project_count:
            raise serializers.ValidationError({"max_verified_project_count": "Maximum value must be greater than or equal to minimum value."})

        return attrs



class CalculateFixedSystemFieldsRequestSerializer(serializers.Serializer):
    """Request body for CalculateFixedSystemFieldsAPIView. Plain
    serializers.Serializer (not a ModelSerializer) since this isn't a
    model — it only exists so drf-spectacular can render the payload
    shape in Swagger; the view still reads request.data directly.
    """

    professional_id = serializers.IntegerField(
        help_text="ProfessionalProfile id to recalculate fixed fields for. "
        "Scoped fields (Calendar Experience, Verified Field Days, Verified "
        "Project Count, Highest Authority Reached) run for every scope the "
        "professional already has a ProfessionalScope row for; no scope "
        "can be seeded through this endpoint."
    )


        