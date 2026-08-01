from django.core.exceptions import ValidationError
from rest_framework import serializers

from accounts.models import ConsentRecord, RegistrationApplication, UserTbl
from tenancy.models import Tenant


class UserTblSerializer(serializers.ModelSerializer):
    
    # def to_internal_value(self, data):
    #     allowed_fields = set(self.fields.keys())

    #     filtered_data = {
    #         key: value
    #         for key, value in data.items()
    #         if key in allowed_fields
    #     }

    #     return super().to_internal_value(filtered_data)
    
    class Meta:
        model = UserTbl
        fields = "__all__"
        read_only_fields = ["public_id", "date_joined", "updated_at", "last_login"]

    def create(self, validated_data):
        roles = validated_data.pop("role", [])
        user = super().create(validated_data)
        if roles:
            user.role.set(roles)
        return user

    def update(self, instance, validated_data):
        roles = validated_data.pop("role", None)
        user = super().update(instance, validated_data)
        if roles is not None:
            user.role.set(roles)
        return user


class RegistrationApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationApplication
        fields = "__all__"
        read_only_fields = ["public_id", "created_at", "updated_at"]


class ConsentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentRecord
        fields = "__all__"
        read_only_fields = ["created_at"]


class LoginSerializer(serializers.Serializer):
    tenant = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Tenant id or portal slug used for tenant-scoped login.",
    )    
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False)

    def _resolve_tenant(self, tenant_value):
        if not tenant_value:
            return None

        tenant_value = str(tenant_value).strip()
        if not tenant_value:
            return None

        tenant = None
        for lookup in (
            {"public_id": tenant_value},
            {"id": tenant_value},
            {"portal_slug": tenant_value},
        ):
            if tenant:
                break
            try:
                tenant = Tenant.objects.filter(**lookup).first()
            except (ValueError, ValidationError):
                continue

        return tenant

    def validate(self, attrs):
        tenant_value = (attrs.get("tenant") or "").strip()
        email = (attrs.get("email") or "").strip().lower()
        password = attrs.get("password") or ""

        tenant = self._resolve_tenant(tenant_value) if tenant_value else None

        if tenant is not None:
            users = list(UserTbl.objects.filter(tenant=tenant, email__iexact=email))
        else:
            users = list(
                UserTbl.objects.filter(
                    email__iexact=email,
                    role__roles_for="super admin",
                )
            )

        if not users:
            raise serializers.ValidationError({"email": ["Invalid credentials."]})

        if len(users) > 1:
            raise serializers.ValidationError(
                {
                    "email": [
                        "Multiple super admin accounts matched this email. Please provide tenant credentials instead."
                    ]
                }
            )

        user = users[0]

        if not user:
            raise serializers.ValidationError({"email": ["Invalid credentials."]})        

        if not user.is_active:
            raise serializers.ValidationError({"email": ["This account is inactive."]})

        if user.approval_status != UserTbl.ApprovalStatus.APPROVED:
            raise serializers.ValidationError(
                {"email": ["This account is not approved for login."]}
            )
            
        if not user.check_password(password):
                    raise serializers.ValidationError({"password": ["Invalid credentials."]})

        attrs["user"] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    pass

