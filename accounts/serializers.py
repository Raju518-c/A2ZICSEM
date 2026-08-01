import json
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import F
from django.utils import timezone
from rest_framework import serializers

from accounts.models import (
    ConsentRecord,
    OTPVerification,
    RegistrationApplication,
    UserTbl,
    validate_mobile_number,
)
from tenancy.models import Tenant


def _resolve_tenant(tenant_value):
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


def _resolve_user(tenant_value, email):
    tenant = _resolve_tenant(tenant_value) if tenant_value else None
    email = (email or "").strip().lower()

    if tenant is not None:
        users = list(UserTbl.objects.filter(tenant=tenant, email__iexact=email))
    else:
        users = list(
            UserTbl.objects.filter(email__iexact=email, role__roles_for="super admin")
        )

    if len(users) == 1:
        return users[0]
    return None

class AccountRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    mobile_country_code = serializers.CharField(required=True, allow_blank=False)
    mobile_number = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    two_factor_preference = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class ProfileRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, allow_blank=True)
    middle_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    preferred_name = serializers.CharField(required=False, allow_blank=True)
    country_of_residence = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    time_zone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    primary_industry = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    primary_scope = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    career_stage = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    current_job_title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    total_experience_band = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    highest_qualification = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    name_order = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    existing_resume = serializers.BooleanField(required=False, default=False)
    
    


class ConsentRegistrationSerializer(serializers.Serializer):
    terms = serializers.BooleanField(required=False, default=False)
    privacy = serializers.BooleanField(required=False, default=False)
    resume_processing = serializers.BooleanField(required=False, default=False)
    marketing = serializers.BooleanField(required=False, default=False)


class RegisterRequestSerializer(serializers.Serializer):
    tenant_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    tenant = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    account = AccountRegistrationSerializer(required=True)
    profile = ProfileRegistrationSerializer(required=False, default={})
    consent = ConsentRegistrationSerializer(required=False, default={})
    resume = serializers.FileField(required=False, allow_null=True, write_only=True)
    profile_photo = serializers.FileField(required=False, allow_null=True, write_only=True)

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            data = data.dict() if hasattr(data, "dict") else data

        normalized_data = {}
        for key, value in data.items():
            if key in {"account", "profile", "consent"} and isinstance(value, str):
                try:
                    normalized_data[key] = json.loads(value)
                except json.JSONDecodeError:
                    normalized_data[key] = value
            else:
                normalized_data[key] = value

        return super().to_internal_value(normalized_data)


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


class OTPRequestSerializer(serializers.Serializer):
    """Issues an OTP. One endpoint for all otp_type values:
    EMAIL/MOBILE cover both initial verification and re-verification of a
    changed address (pass new_value); LOGIN performs the password check
    and issues a second-factor code when the account has MFA enabled;
    PASSWORD_RESET issues a code to the account's registered email.
    """

    otp_type = serializers.ChoiceField(choices=OTPVerification.OTPType.choices)
    tenant = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Tenant id, public_id, or portal slug.",
    )
    email = serializers.EmailField(help_text="Account's current login email.")
    password = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=False,
        write_only=True,
        help_text="Required only when otp_type=LOGIN.",
    )
    new_value = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text=(
            "Required only for EMAIL/MOBILE when re-verifying a changed "
            "address: the new email, or the new mobile number (digits "
            "only, no country code)."
        ),
    )

    def validate(self, attrs):
        otp_type = attrs["otp_type"]
        user = _resolve_user(attrs.get("tenant"), attrs["email"])
        new_value = (attrs.get("new_value") or "").strip()

        if otp_type == OTPVerification.OTPType.PASSWORD_RESET:
            # Do not reveal whether the account exists.
            attrs["user"] = user
            attrs["sent_to"] = user.email if user else None
            return attrs

        if user is None:
            raise serializers.ValidationError({"email": ["No matching account found."]})

        if otp_type == OTPVerification.OTPType.LOGIN:
            password = attrs.get("password") or ""
            if not password:
                raise serializers.ValidationError({"password": ["Password is required."]})
            if not user.is_active:
                raise serializers.ValidationError({"email": ["This account is inactive."]})
            if user.approval_status != UserTbl.ApprovalStatus.APPROVED:
                raise serializers.ValidationError(
                    {"email": ["This account is not approved for login."]}
                )
            if not user.check_password(password):
                raise serializers.ValidationError({"password": ["Invalid credentials."]})
            if user.mfa_method == UserTbl.MfaMethod.NONE:
                raise serializers.ValidationError(
                    {"otp_type": ["MFA is not enabled for this account."]}
                )
            if user.mfa_method == UserTbl.MfaMethod.AUTHENTICATOR:
                raise serializers.ValidationError(
                    {"otp_type": ["This account uses an authenticator app, not OTP."]}
                )
            sent_to = (
                user.email
                if user.mfa_method == UserTbl.MfaMethod.EMAIL
                else f"{user.mobile_country_code}{user.mobile_number}"
            )

        elif otp_type == OTPVerification.OTPType.EMAIL:
            sent_to = new_value.lower() if new_value else user.email
            if new_value:
                serializers.EmailField().run_validation(new_value)
                if (
                    UserTbl.objects.filter(tenant=user.tenant, email__iexact=new_value)
                    .exclude(pk=user.pk)
                    .exists()
                ):
                    raise serializers.ValidationError(
                        {"new_value": ["This email is already in use."]}
                    )

        elif otp_type == OTPVerification.OTPType.MOBILE:
            number = new_value if new_value else user.mobile_number
            if new_value:
                try:
                    validate_mobile_number(new_value)
                except ValidationError as exc:
                    raise serializers.ValidationError({"new_value": exc.messages}) from exc
                if (
                    UserTbl.objects.filter(
                        tenant=user.tenant,
                        mobile_country_code=user.mobile_country_code,
                        mobile_number=new_value,
                    )
                    .exclude(pk=user.pk)
                    .exists()
                ):
                    raise serializers.ValidationError(
                        {"new_value": ["This mobile number is already in use."]}
                    )
            # Delivery needs the calling code; the digits-only number is
            # recovered from this on verify (see OTPVerifyAPIView).
            sent_to = f"{user.mobile_country_code}{number}"
        else:
            raise serializers.ValidationError({"otp_type": ["Unsupported OTP type."]})

        attrs["user"] = user
        attrs["sent_to"] = sent_to
        return attrs


class OTPVerifySerializer(serializers.Serializer):
    """Verifies an OTP and applies the effect for its otp_type: marks
    email/mobile verified, resets the password, or completes login.
    """

    otp_type = serializers.ChoiceField(choices=OTPVerification.OTPType.choices)
    tenant = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Tenant id, public_id, or portal slug.",
    )
    email = serializers.EmailField(help_text="Account's current login email.")
    otp = serializers.CharField(max_length=6, min_length=6, trim_whitespace=False)
    new_password = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=False,
        write_only=True,
        help_text="Required only when otp_type=PASSWORD_RESET.",
    )

    def validate(self, attrs):
        otp_type = attrs["otp_type"]
        user = _resolve_user(attrs.get("tenant"), attrs["email"])
        generic_error = {"otp": ["Invalid or expired code."]}

        if user is None:
            raise serializers.ValidationError(generic_error)

        row = (
            OTPVerification.objects.filter(
                user=user,
                otp_type=otp_type,
                is_used=False,
                expires_at__gt=timezone.now(),
            )
            .order_by("-created_at")
            .first()
        )

        if row is None or row.attempts >= OTPVerification.MAX_ATTEMPTS:
            raise serializers.ValidationError(generic_error)

        if not row.check_otp(attrs["otp"]):
            OTPVerification.objects.filter(pk=row.pk).update(attempts=F("attempts") + 1)
            raise serializers.ValidationError(generic_error)

        if otp_type == OTPVerification.OTPType.PASSWORD_RESET:
            new_password = attrs.get("new_password") or ""
            try:
                validate_password(new_password, user=user)
            except ValidationError as exc:
                raise serializers.ValidationError({"new_password": exc.messages}) from exc

        # otp_row is not marked used here: the view applies it and the
        # side effect (email/mobile/password/login) inside one
        # transaction, so a downstream failure leaves the OTP usable.
        attrs["user"] = user
        attrs["otp_row"] = row
        return attrs

