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