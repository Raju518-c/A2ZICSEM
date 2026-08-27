import hashlib
import json

from django.db import transaction
from rest_framework import serializers
from django.utils import timezone
from accounts.models import UserTbl, roles
from catalog.models import ReferenceValue

from .models import *
from django.http import QueryDict

class TenantSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(required=False, allow_null=True, style={"base_template": "file.html"})
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
    logo = serializers.ImageField(required=False, allow_null=True, style={"base_template": "file.html"})
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
    approved_at = serializers.DateTimeField(required=False,allow_null=True,)
    is_active = serializers.BooleanField(required=False)
    is_staff = serializers.BooleanField(required=False)
    is_superuser = serializers.BooleanField(required=False)


class TenantCombinedCreateSerializer(serializers.Serializer):
    tenant = TenantCreateInputSerializer(required=True)
    operations = TenantOperationCreateInputSerializer(many=True, required=False, default=list)
    role = RoleCreateInputSerializer(required=False, default=dict)
    user = UserCreateInputSerializer(required=True)
    logo = serializers.ImageField(required=False, allow_null=True, write_only=True, style={"base_template": "file.html"})

    def _parse_json_value(self, value):
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return value
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                # If raw contains multiple JSON objects separated by commas/newlines
                # (e.g. '{...},\n{...}'), try to wrap them into a JSON array and parse.
                try:
                    wrapped = f"[{raw}]"
                    return json.loads(wrapped)
                except json.JSONDecodeError:
                    # fall through and re-raise original error
                    raise
        return value


    # def to_internal_value(self, data):

    #     if isinstance(data, QueryDict):
    #         data = dict(data)

    #     # for key in ("tenant", "operations", "role", "user", "logo"):
    #     #     if key in data and isinstance(data.get(key), (list, tuple)):
    #     #         items = data.get(key)
    #     #         if len(items) == 1:
    #     #             data[key] = items[0]
        
    #     for key in ("tenant", "operations", "role", "user", "logo"):
    #         if key in data and isinstance(data[key], list):
    #             if len(data[key]) == 1:
    #                 data[key] = data[key][0]

    #     print("AFTER UNWRAP:", data)

    #     # Unwrap single-item lists from QueryDict (multipart form fields)
    #     # for key in ("tenant", "operations", "role", "user", "logo"):
    #     #     if key in data and isinstance(data.get(key), (list, tuple)):
    #     #         items = data.get(key)
    #     #         if len(items) == 1:
    #     #             data[key] = items[0]

    #     if "tenant" in data and isinstance(data.get("tenant"), str):
    #         data["tenant"] = self._parse_json_value(data["tenant"])

    #     if "operations" in data and isinstance(data.get("operations"), str):
    #         parsed_operations = self._parse_json_value(data["operations"])
    #         if isinstance(parsed_operations, dict):
    #             parsed_operations = [parsed_operations]
    #         data["operations"] = parsed_operations

    #     if "role" in data and isinstance(data.get("role"), str):
    #         data["role"] = self._parse_json_value(data["role"])

    #     if "user" in data and isinstance(data.get("user"), str):
    #         data["user"] = self._parse_json_value(data["user"])

    #     # If logo was uploaded via request.FILES, ensure it's set
    #     if "logo" not in data and self.context.get("files") and "logo" in self.context["files"]:
    #         data["logo"] = self.context["files"]["logo"]

    #     print("AFTER JSON:", data)
    #     return super().to_internal_value(data)

    def to_internal_value(self, data):

        # Convert QueryDict -> normal dict
        if isinstance(data, QueryDict):
            data = dict(data)

        # Unwrap single-item lists
        for key in ("tenant", "operations", "role", "user", "logo"):
            if key in data and isinstance(data[key], list):
                if len(data[key]) == 1:
                    data[key] = data[key][0]

        # Parse JSON strings
        if isinstance(data.get("tenant"), str):
            data["tenant"] = self._parse_json_value(data["tenant"])

        if isinstance(data.get("operations"), str):
            parsed_operations = self._parse_json_value(data["operations"])

            if isinstance(parsed_operations, dict):
                parsed_operations = [parsed_operations]

            data["operations"] = parsed_operations

        if isinstance(data.get("role"), str):
            data["role"] = self._parse_json_value(data["role"])

        if isinstance(data.get("user"), str):
            data["user"] = self._parse_json_value(data["user"])

        print("FINAL DATA:", data)

        return super().to_internal_value(data)
    
    
    # def create(self, validated_data):
    #     tenant_data = validated_data["tenant"]
    #     operations_data = validated_data.get("operations", [])
    #     role_data = validated_data.get("role") or {}
    #     user_data = validated_data["user"]
    #     logo_file = validated_data.get("logo")

    #     with transaction.atomic():
    #         approval_status = user_data.get(
    #             "approval_status",
    #             UserTbl.ApprovalStatus.APPROVED
    #         )

    #         approved_at = user_data.get("approved_at")

    #         if (
    #             approval_status == UserTbl.ApprovalStatus.APPROVED
    #             and approved_at is None
    #         ):
    #             approved_at = timezone.now()

    #         admin_user = UserTbl.objects.create(
    #             email=user_data["email"].strip().lower(),
    #             mobile_country_code=user_data["mobile_country_code"],
    #             mobile_number=user_data["mobile_number"],
    #             password=user_data["password"],
    #             approval_status=approval_status,
    #             approved_at=approved_at,
    #             is_active=user_data.get("is_active", True),
    #             is_staff=user_data.get("is_staff", True),
    #             is_superuser=user_data.get("is_superuser", False),
    #         )

    #         tenant_payload = dict(tenant_data)
    #         if logo_file is not None:
    #             tenant_payload["logo"] = logo_file
    #         tenant_payload["created_by"] = tenant_payload.get("created_by").pk
    #         tenant = Tenant.objects.create(**tenant_payload)
    #         admin_user.tenant = tenant
    #         admin_user.save(update_fields=["tenant", "updated_at"])

    #         role_code = (role_data.get("code") or user_data.get("role") or "Admin").strip()
    #         role_name = (role_data.get("name") or role_code or "Admin").strip()
    #         role_for = (role_data.get("roles_for") or "tenant admin").strip()

    #         role_obj, _ = roles.objects.get_or_create(
    #             code=role_code,
    #             tenant=tenant,
    #             defaults={"name": role_name, "roles_for": role_for},
    #         )
    #         admin_user.role.add(role_obj)

    #         created_operations = []
    #         for operation_data in operations_data:
    #             operation_payload = {
    #                 "tenant": tenant.pk,
    #                 "industry": operation_data.get("industry").pk,
    #                 "country_code": operation_data.get("country_code"),
    #                 "region_name": operation_data.get("region_name", ""),
    #                 "is_registration_enabled": operation_data.get(
    #                     "is_registration_enabled", True
    #                 ),
    #                 "is_active": operation_data.get("is_active", True),
    #                 "effective_from": operation_data.get("effective_from"),
    #                 "effective_to": operation_data.get("effective_to"),
    #                 "created_by": admin_user.pk,
    #             }
    #             created_operations.append(TenantOperation.objects.create(**operation_payload))

    #     return {
    #         "tenant": tenant,
    #         "operations": created_operations,
    #         "role": role_obj,
    #         "user": admin_user,
    #     }

    def create(self, validated_data):
        tenant_data = validated_data["tenant"]
        operations_data = validated_data.get("operations", [])
        role_data = validated_data.get("role") or {}
        user_data = validated_data["user"]
        logo_file = validated_data.get("logo")

        with transaction.atomic():

            approval_status = user_data.get(
                "approval_status",
                UserTbl.ApprovalStatus.APPROVED
            )

            approved_at = user_data.get("approved_at")

            if (
                approval_status == UserTbl.ApprovalStatus.APPROVED
                and approved_at is None
            ):
                approved_at = timezone.now()

            admin_user = UserTbl.objects.create(
                email=user_data["email"].strip().lower(),
                mobile_country_code=user_data["mobile_country_code"],
                mobile_number=user_data["mobile_number"],
                password=user_data["password"],

                approval_status=approval_status,
                approved_at=approved_at,

                is_active=user_data.get("is_active", True),
                is_staff=user_data.get("is_staff", True),
                is_superuser=user_data.get("is_superuser", False),
            )

            tenant_payload = dict(tenant_data)

            if logo_file is not None:
                tenant_payload["logo"] = logo_file

            tenant = Tenant.objects.create(**tenant_payload)

            admin_user.tenant = tenant
            admin_user.save(update_fields=["tenant", "updated_at"])

            role_code = (
                role_data.get("code")
                or user_data.get("role")
                or "Admin"
            ).strip()

            role_name = (
                role_data.get("name")
                or role_code
                or "Admin"
            ).strip()

            role_for = (
                role_data.get("roles_for")
                or "tenant admin"
            ).strip()

            role_obj, _ = roles.objects.get_or_create(
                code=role_code,
                tenant=tenant,
                defaults={
                    "name": role_name,
                    "roles_for": role_for,
                },
            )

            admin_user.role.add(role_obj)

            created_operations = []

            for operation_data in operations_data:
                created_operations.append(
                    TenantOperation.objects.create(
                        tenant=tenant,
                        industry=operation_data["industry"],
                        country_code=operation_data["country_code"],
                        region_name=operation_data.get("region_name", ""),
                        is_registration_enabled=operation_data.get(
                            "is_registration_enabled",
                            True,
                        ),
                        is_active=operation_data.get(
                            "is_active",
                            True,
                        ),
                        effective_from=operation_data.get(
                            "effective_from"
                        ),
                        effective_to=operation_data.get(
                            "effective_to"
                        ),
                        created_by=admin_user,
                    )
                )

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


class TenantLegalEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantLegalEntity
        fields = "__all__"


class TenantTaxRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantTaxRegistration
        fields = "__all__"


class TenantDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantDomain
        fields = "__all__"
        

class TenantLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantLocation
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]        
    
class TenantAuthorisedRepresentativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantAuthorisedRepresentative
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class TenantContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantContact
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class TenantVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantVerification
        fields = "__all__"
        read_only_fields = ["created_at"]


class TenantSubmitSerializer(serializers.Serializer):
    """No input fields. Completeness is checked server-side against the
    tenant's own related tables (legal entity, location, representative,
    document, legal acceptance, operation) — nothing is accepted from the
    request body.
    """
    pass


class TenantResubmitSerializer(serializers.Serializer):
    """No input fields. Re-runs the same completeness check as submit;
    the corrected data itself was already saved via the individual
    per-table endpoints before this is called.
    """
    pass


class TenantReviewDecisionSerializer(serializers.Serializer):
    """Superadmin review decision for a tenant application.

    Accepts:
      - status: APPROVED / REJECTED / RETURNED (from TenantVerification.Status)
      - reason: Required when status is REJECTED or RETURNED
      - risk_classification: Optional, defaults to STANDARD
      - next_review_date: Optional, date for periodic review
    """

    status = serializers.ChoiceField(
        choices=[
            ("APPROVED", "Approved"),
            ("REJECTED", "Rejected"),
            ("RETURNED", "Returned"),
        ],
        required=True,
    )
    reason = serializers.CharField(required=False, allow_blank=True, default="")
    risk_classification = serializers.ChoiceField(
        choices=[
            ("LOW", "Low"),
            ("STANDARD", "Standard"),
            ("ENHANCED_REVIEW", "Enhanced Review"),
            ("RESTRICTED", "Restricted"),
        ],
        required=False,
        default="STANDARD",
    )
    next_review_date = serializers.DateField(required=False, allow_null=True, default=None)

    def validate(self, data):
        status = data.get("status")
        reason = data.get("reason", "").strip()
        if status in {"REJECTED", "RETURNED"} and not reason:
            raise serializers.ValidationError(
                {"reason": "Reason is required when status is REJECTED or RETURNED."}
            )
        return data


class Stage1TenantDetailsSerializer(serializers.Serializer):
    """Read-only bundle of everything submitted for a tenant's Stage 1
    application — the Tenant row itself plus every related table from
    the PDF's Stage 1 list, queried directly by tenant= (not through a
    reverse-accessor name) same as _check_tenant_application_complete.
    Mirrors accounts.Stage1DetailsSerializer's shape for the
    professional side.
    """

    tenant = serializers.SerializerMethodField()
    founding_admin = serializers.SerializerMethodField()
    legal_entities = serializers.SerializerMethodField()
    tax_registrations = serializers.SerializerMethodField()
    locations = serializers.SerializerMethodField()
    authorised_representatives = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    legal_acceptances = serializers.SerializerMethodField()
    operations = serializers.SerializerMethodField()

    def get_tenant(self, obj):
        return TenantSerializer(obj).data

    def get_founding_admin(self, obj):
        admin = obj.created_by
        if admin is None:
            return None
        return {
            "id": admin.id,
            "email": admin.email,
            "mobile_country_code": admin.mobile_country_code,
            "mobile_number": admin.mobile_number,
            "approval_status": admin.approval_status,
        }

    def get_legal_entities(self, obj):
        return TenantLegalEntitySerializer(
            TenantLegalEntity.objects.filter(tenant=obj).order_by("-created_at"), many=True
        ).data

    def get_tax_registrations(self, obj):
        return TenantTaxRegistrationSerializer(
            TenantTaxRegistration.objects.filter(tenant=obj).order_by("-created_at"), many=True
        ).data

    def get_locations(self, obj):
        return TenantLocationSerializer(
            TenantLocation.objects.filter(tenant=obj).order_by("-created_at"), many=True
        ).data

    def get_authorised_representatives(self, obj):
        return TenantAuthorisedRepresentativeSerializer(
            TenantAuthorisedRepresentative.objects.filter(tenant=obj).order_by("-created_at"), many=True
        ).data

    def get_documents(self, obj):
        return TenantDocumentSerializer(
            TenantDocument.objects.filter(tenant=obj).order_by("-created_at"), many=True
        ).data

    def get_legal_acceptances(self, obj):
        return TenantLegalAcceptanceSerializer(
            TenantLegalAcceptance.objects.filter(tenant=obj).order_by("-created_at"), many=True
        ).data

    def get_operations(self, obj):
        return TenantOperationSerializer(
            TenantOperation.objects.filter(tenant=obj).order_by("-created_at"), many=True
        ).data


class TenantDocumentSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        uploaded_file = validated_data["file"]
        digest = hashlib.sha256()

        for chunk in uploaded_file.chunks():
            digest.update(chunk)

        uploaded_file.seek(0)
        validated_data["file_hash"] = digest.hexdigest()
        return super().create(validated_data)

    class Meta:
        model = TenantDocument
        fields = "__all__"
        read_only_fields = ["file_hash", "created_at", "updated_at"]
        


class TenantLegalAcceptanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantLegalAcceptance
        fields = "__all__"
        read_only_fields = ["created_at"]


class TenantLegalSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantLegalSettings
        fields = "__all__"
        read_only_fields = ["updated_at"]


class TenantNdaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantNda
        fields = "__all__"
        read_only_fields = ["created_at"]


class TenantSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantSettings
        fields = "__all__"
        read_only_fields = ["updated_at"]

class TenantSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantSubscription
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class TenantModuleEntitlementSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantModuleEntitlement
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

class TenantBrandingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantBranding
        fields = "__all__"
        read_only_fields = ["updated_at"]


class TenantReportTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantReportTemplate
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class TenantSecuritySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantSecuritySettings
        fields = "__all__"
        read_only_fields = ["updated_at"]


class TenantIPRestrictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantIPRestriction
        fields = "__all__"
        read_only_fields = ["created_at"]


class TenantIntegrationSerializer(serializers.ModelSerializer):
    # Docstring is explicit: "Never exported; encrypted at rest." That's a
    # behavioral rule, not just a PII classification tag — write_only means
    # it can be set on create/update but is never present in any response.
    secret_reference = serializers.CharField(write_only=True)

    class Meta:
        model = TenantIntegration
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class TenantBillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantBilling
        fields = "__all__"
        read_only_fields = ["updated_at"]



class TenantInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantInvitation
        fields = "__all__"
        read_only_fields = ["sent_at"]


class TenantWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantWorkflow
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class TenantWorkflowStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantWorkflowStep
        fields = "__all__"


class TenantOperationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantOperationLog
        fields = "__all__"
        read_only_fields = ["started_at"]


class TenantTerminologySerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantTerminology
        fields = "__all__"


class TenantNumberingConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantNumberingConfig
        fields = "__all__"


class TenantApprovalMatrixSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantApprovalMatrix
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class TenantNotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantNotificationSettings
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class ConflictOfInterestDeclarationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConflictOfInterestDeclaration
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class DataExportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataExportRequest
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
        

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class ProjectRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectRequirement
        fields = "__all__"


class ProjectRequirementScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectRequirementScope
        fields = "__all__"


class ProjectCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCandidate
        fields = "__all__"


class DisclosureRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisclosureRequest
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class CandidateConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateConsent
        fields = "__all__"
        read_only_fields = ["decided_at"]


class ProjectPlacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPlacement
        fields = "__all__"


class ProjectScopeLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectScopeLink
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


        






