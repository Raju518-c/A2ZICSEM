from django.db import transaction
from rest_framework import serializers

from accounts.models import UserTbl, roles
from catalog.models import ReferenceValue

from .models import *


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = "__all__"


class TenantOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantOperation
        fields = "__all__"


class TenantCreateInputSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    legal_name = serializers.CharField(required=False, allow_blank=True)
    code = serializers.CharField(required=True)
    portal_slug = serializers.CharField(required=True)
    custom_domain = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    status = serializers.CharField(required=False, allow_blank=True)
    registration_enabled = serializers.BooleanField(required=False)
    login_enabled = serializers.BooleanField(required=False)
    default_timezone = serializers.CharField(required=False, allow_blank=True)
    default_currency = serializers.CharField(required=False, allow_blank=True)
    contact_email = serializers.EmailField(required=False, allow_blank=True)
    contact_phone = serializers.CharField(required=False, allow_blank=True)
    settings = serializers.JSONField(required=False, default=dict)
    branding = serializers.JSONField(required=False, default=dict)
    logo = serializers.ImageField(required=False, allow_null=True)
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=UserTbl.objects.all(), required=True
    )


class TenantOperationCreateInputSerializer(serializers.Serializer):
    industry = serializers.PrimaryKeyRelatedField(queryset=ReferenceValue.objects.all(), required=True)
    country_code = serializers.CharField(required=True)
    region_name = serializers.CharField(required=False, allow_blank=True)
    is_registration_enabled = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    effective_from = serializers.DateField(required=False, allow_null=True)
    effective_to = serializers.DateField(required=False, allow_null=True)


class RoleCreateInputSerializer(serializers.Serializer):
    code = serializers.CharField(required=False, allow_blank=True)
    name = serializers.CharField(required=False, allow_blank=True)
    roles_for = serializers.CharField(required=False, allow_blank=True)


class UserCreateInputSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    mobile_country_code = serializers.CharField(required=True)
    mobile_number = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    role = serializers.CharField(required=False, allow_blank=True)
    approval_status = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)
    is_staff = serializers.BooleanField(required=False)
    is_superuser = serializers.BooleanField(required=False)


class TenantCombinedCreateSerializer(serializers.Serializer):
    tenant = TenantCreateInputSerializer(required=True)
    operations = serializers.JSONField(required=False, default=list)
    role = RoleCreateInputSerializer(required=False, default=dict)
    user = UserCreateInputSerializer(required=True)

    def validate_operations(self, value):
        if value in (None, ""):
            return []

        if isinstance(value, dict):
            items = [value]
        elif isinstance(value, list):
            items = value
        else:
            raise serializers.ValidationError("operations must be an object or a list of objects.")

        validated_items = []
        for item in items:
            if not isinstance(item, dict):
                raise serializers.ValidationError("each operation must be an object.")

            operation_serializer = TenantOperationCreateInputSerializer(data=item)
            operation_serializer.is_valid(raise_exception=True)
            validated_items.append(operation_serializer.validated_data)

        return validated_items

    def create(self, validated_data):
        tenant_data = validated_data["tenant"]
        operations_data = validated_data.get("operations", [])
        role_data = validated_data.get("role") or {}
        user_data = validated_data["user"]

        with transaction.atomic():
            admin_user = UserTbl.objects.create(
                email=user_data["email"].strip().lower(),
                mobile_country_code=user_data["mobile_country_code"],
                mobile_number=user_data["mobile_number"],
                password=user_data["password"],
                approval_status=user_data.get(
                    "approval_status", UserTbl.ApprovalStatus.APPROVED
                ),
                is_active=user_data.get("is_active", True),
                is_staff=user_data.get("is_staff", True),
                is_superuser=user_data.get("is_superuser", False),
            )

            tenant_payload = dict(tenant_data)
            tenant_payload["created_by"] = tenant_payload.get("created_by").pk
            tenant = Tenant.objects.create(**tenant_payload)
            admin_user.tenant = tenant
            admin_user.save(update_fields=["tenant", "updated_at"])

            role_code = (role_data.get("code") or user_data.get("role") or "Admin").strip()
            role_name = (role_data.get("name") or role_code or "Admin").strip()
            role_for = (role_data.get("roles_for") or "tenant admin").strip()

            role_obj, _ = roles.objects.get_or_create(
                code=role_code,
                tenant=tenant,
                defaults={"name": role_name, "roles_for": role_for},
            )
            admin_user.role.add(role_obj)

            created_operations = []
            for operation_data in operations_data:
                operation_payload = {
                    "tenant": tenant.pk,
                    "industry": operation_data.get("industry").pk,
                    "country_code": operation_data.get("country_code"),
                    "region_name": operation_data.get("region_name", ""),
                    "is_registration_enabled": operation_data.get(
                        "is_registration_enabled", True
                    ),
                    "is_active": operation_data.get("is_active", True),
                    "effective_from": operation_data.get("effective_from"),
                    "effective_to": operation_data.get("effective_to"),
                    "created_by": admin_user.pk,
                }
                created_operations.append(TenantOperation.objects.create(**operation_payload))

        return {
            "tenant": tenant,
            "operations": created_operations,
            "role": role_obj,
            "user": admin_user,
        }


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

