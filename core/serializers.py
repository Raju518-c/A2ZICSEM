from datetime import date

from django.db import models
from django.db import transaction
from rest_framework import serializers

from accounts.models import *
from competency.models import *
from catalog.models import *
from evidence.models import *
from experience.models import *
from governance.models import *
from professionals.models import *
from resumes.models import *
from tenancy.models import *

from competency.models import *
from .models import *

class DynamicTableQueryItemSerializer(serializers.Serializer):
    table = serializers.CharField(required=True)
    includes = serializers.DictField(required=False, default=dict, allow_empty=True)
    excludes = serializers.DictField(required=False, default=dict, allow_empty=True)    
    return_fields = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
        allow_empty=True,
    )


class DynamicTableQueryListSerializer(serializers.ListSerializer):
    child = DynamicTableQueryItemSerializer()



class CoreRegistrationApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationApplication
        fields = "__all__"



class CoreConsentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentRecord
        fields = "__all__"


class CoreUserTblSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTbl
        fields = "__all__"


class CoreEmploymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmploymentRecord
        fields = "__all__"



class CoreScopeResponseSerializer(serializers.ModelSerializer):    
    class Meta:
        model = ScopeResponse
        fields = "__all__"

class CoreProjectScopeSerializer(serializers.ModelSerializer):
    scope_responses = CoreScopeResponseSerializer(many=True, read_only=True)
    class Meta:
        model = ProjectScope
        fields = "__all__"


class CoreProjectRecordSerializer(serializers.ModelSerializer):
    project_scopes = CoreProjectScopeSerializer(many=True, read_only=True)
    class Meta:
        model = ProjectRecord
        fields = "__all__"


class CoreCredentialRecordItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CredentialRecordItem
        fields = "__all__"


class CoreCredentialRecordSerializer(serializers.ModelSerializer):
    items = CoreCredentialRecordItemSerializer(many=True, read_only=True)

    class Meta:
        model = CredentialRecord
        fields = "__all__"


class CoreCapabilityRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapabilityRecord
        fields = "__all__"


class CoreContactRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactRecord
        fields = "__all__"


class CoreEvidenceDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenceDocument
        fields = "__all__"


class CoreProfessionalReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalReview
        fields = "__all__"


class CoreProfessionalScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalScope
        fields = "__all__"
        
class CoreProfessionalProfileRelatedSerializer(serializers.ModelSerializer):
    user = CoreUserTblSerializer(read_only=True)
    registration = CoreRegistrationApplicationSerializer(read_only=True)
    consent_records = CoreConsentRecordSerializer(many=True, read_only=True)
    employment_records = CoreEmploymentRecordSerializer(many=True, read_only=True)
    project_records = CoreProjectRecordSerializer(many=True, read_only=True)
    credentials = CoreCredentialRecordSerializer(many=True, read_only=True)
    capabilities = CoreCapabilityRecordSerializer(many=True, read_only=True)
    contacts = CoreContactRecordSerializer(many=True, read_only=True)
    evidence_documents = CoreEvidenceDocumentSerializer(many=True, read_only=True)
    reviews = CoreProfessionalReviewSerializer(many=True, read_only=True)
    scopes = CoreProfessionalScopeSerializer(many=True, read_only=True)

    class Meta:
        model = ProfessionalProfile
        fields = (
            "id",
            "public_id",
            "tenant",
            "user",
            "registration",
            "consent_records",
            "registration_application",
            "profile_status",
            "current_classification",
            "classification_status",
            "classified_by",
            "classified_at",
            "classification_ruleset_version",
            "profile_version",
            "completion_percent",
            "legal_full_name",
            "display_name",
            "first_name",
            "middle_name",
            "last_name",
            "preferred_name",
            "name_display_order",
            "date_of_birth",
            "gender",
            "nationalities",
            "country_of_residence",
            "city",
            "timezone",
            "personal_email",
            "primary_phone",
            "linkedin_url",
            "existing_resume",
            "profile_photo_evidence",
            "photo_resume_visibility",
            "primary_industry",
            "primary_scope",
            "self_declared_career_stage",
            "current_job_title",
            "initial_experience_band",
            "highest_qualification_level",
            "headline",
            "summary",
            "key_strengths",
            "primary_role",
            "additional_roles",
            "summary_source",
            "availability_status",
            "available_from",
            "notice_period_days",
            "engagement_types",
            "preferred_locations",
            "offshore_ready",
            "rate_type",
            "expected_rate",
            "rate_currency",
            "ppe_sizes",
            "submitted_at",
            "approved_at",
            "employment_records",
            "project_records",
            "credentials",
            "capabilities",
            "contacts",
            "evidence_documents",
            "reviews",
            "scopes",
            "created_at",
            "updated_at",
        )


# Backward-compatible aliases for the project-wide serializer usage that already
# exists in other apps.
ProfessionalProfileSerializer = CoreProfessionalProfileRelatedSerializer



class TenantRegistrationInviteSerializer(serializers.ModelSerializer):

    class Meta:
        model = TenantRegistrationInvite

        fields = [
            "id",
            "email",
            "invitation_date_time",
            "is_registered",
            "registered_date_time",
            "invitation_token",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "invitation_date_time",
            "is_registered",
            "registered_date_time",
            "invitation_token",
            "created_at",
            "updated_at",
        ]

class TenantRegistrationInviteCreateSerializer(serializers.Serializer):

    email = serializers.EmailField(
        required=True
    )

    registration_url = serializers.URLField(
        required=True
    )

    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    registered_industry = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=255
    )

    def validate_email(self, value):
        return value.lower().strip()

    def validate_registration_url(self, value):
        return value.rstrip("/")


