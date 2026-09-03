from rest_framework import serializers
from .models import *


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


        