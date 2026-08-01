from rest_framework import serializers

from .models import *


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = "__all__"


class TenantOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantOperation
        fields = "__all__"


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

