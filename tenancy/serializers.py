from rest_framework import serializers

from .models import Tenant, TenantOperation


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = "__all__"


class TenantOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantOperation
        fields = "__all__"


