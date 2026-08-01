from rest_framework import serializers

from .models import FormField, FormModule, ReferenceValue, ScopeCatalog, ScopeModule


class ReferenceValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferenceValue
        fields = "__all__"


class ScopeCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScopeCatalog
        fields = "__all__"
        read_only_fields = ["public_id", "created_at", "updated_at"]


class FormModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormModule
        fields = "__all__"
        read_only_fields = ["public_id", "created_at", "updated_at"]


class ScopeModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScopeModule
        fields = "__all__"
        read_only_fields = ["public_id", "created_at"]


class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = "__all__"
        read_only_fields = ["public_id", "created_at", "updated_at"]
