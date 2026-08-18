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


class DynamicTableQueryItemSerializer(serializers.Serializer):
    table = serializers.CharField(required=True)
    includes = serializers.DictField(required=False, default=dict, allow_empty=True)
    include = serializers.DictField(required=False, default=dict, allow_empty=True, write_only=True)
    excludes = serializers.DictField(required=False, default=dict, allow_empty=True)
    exclude = serializers.DictField(required=False, default=dict, allow_empty=True, write_only=True)
    return_fields = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
        allow_empty=True,
    )


class DynamicTableQueryListSerializer(serializers.ListSerializer):
    child = DynamicTableQueryItemSerializer()


class CoreUserTblSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTbl
        fields = (
            "id",
            "public_id",
            "email",
            "mobile_country_code",
            "mobile_number",
            "tenant",
            "is_candidate",
            "is_mentor",
            "approval_status",
            "is_active",
            "date_joined",
            "updated_at",
        )


class CoreEmploymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmploymentRecord
        fields = "__all__"


class CoreProjectRecordSerializer(serializers.ModelSerializer):
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


class CoreProfessionalProfileRelatedSerializer(serializers.ModelSerializer):
    user = CoreUserTblSerializer(read_only=True)
    employment_records = CoreEmploymentRecordSerializer(many=True, read_only=True)
    project_records = CoreProjectRecordSerializer(many=True, read_only=True)
    credentials = CoreCredentialRecordSerializer(many=True, read_only=True)
    capabilities = CoreCapabilityRecordSerializer(many=True, read_only=True)
    contacts = CoreContactRecordSerializer(many=True, read_only=True)
    evidence_documents = CoreEvidenceDocumentSerializer(many=True, read_only=True)
    reviews = CoreProfessionalReviewSerializer(many=True, read_only=True)

    class Meta:
        model = ProfessionalProfile
        fields = (
            "id",
            "public_id",
            "tenant",
            "user",
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
            "created_at",
            "updated_at",
        )


# Backward-compatible aliases for the project-wide serializer usage that already
# exists in other apps.
ProfessionalProfileSerializer = CoreProfessionalProfileRelatedSerializer

