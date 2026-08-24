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






        