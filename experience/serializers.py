from datetime import date

from django.db import models
from django.db import transaction
from rest_framework import serializers

from catalog.models import FormField, ReferenceValue, ReferencevalueoptionSet, ScopeCatalog
from core.choices import CompletionStatus
from .models import *


class ScopeFormFieldSerializer(serializers.ModelSerializer):
    current_value = serializers.SerializerMethodField()
    response_id = serializers.SerializerMethodField()

    class Meta:
        model = FormField
        fields = (
            "id",
            "field_code",
            "field_label",
            "purpose",
            "data_type",
            "ui_control",
            "is_required",
            "is_repeatable",
            "option_set",
            "options_schema",
            "validation_schema",
            "evidence_rule",
            "sequence",
            "is_active",
            "current_value",
            "response_id",
        )

    def get_current_value(self, obj):
        response_lookup = self.context.get("response_lookup", {})
        response = response_lookup.get(obj.id)
        return response.value if response else None

    def get_response_id(self, obj):
        response_lookup = self.context.get("response_lookup", {})
        response = response_lookup.get(obj.id)
        return response.id if response else None


class EmploymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmploymentRecord
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def validate_employment_type(self, value):
        if value is None:
            return value
        option_type = getattr(value.option_set, "option_type", None)
        if option_type != "ENGAGEMENT_TYPE":
            raise serializers.ValidationError(
                "employment_type must reference a ReferenceValue with option_set=ENGAGEMENT_TYPE."
            )
        return value

    def validate(self, attrs):
        is_current = attrs.get("is_current", getattr(self.instance, "is_current", False))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))

        if is_current and end_date is not None:
            raise serializers.ValidationError(
                {"end_date": "end_date must be empty when is_current is true."}
            )
        if not is_current and end_date is None:
            raise serializers.ValidationError(
                {"end_date": "end_date is required when is_current is false."}
            )
        return attrs






class ProjectRecordSerializer(serializers.ModelSerializer):
    client = serializers.CharField(required=False, allow_blank=True, write_only=True)
    start_date = serializers.DateField(required=False, default=date.today)

    class Meta:
        model = ProjectRecord
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        client_value = self.initial_data.get("client")
        if client_value and "client_name_snapshot" not in attrs:
            attrs["client_name_snapshot"] = client_value
        return attrs

    def create(self, validated_data):
        tenant = self.context.get("tenant")
        professional = self.context.get("professional")
        if not tenant or not professional:
            raise serializers.ValidationError(
                "A tenant and professional context is required to create a project record."
            )

        validated_data["tenant"] = tenant
        validated_data["professional"] = professional
        if "client" in validated_data:
            validated_data.pop("client")

        return super().create(validated_data)

class ScopeResponseInputSerializer(serializers.Serializer):
    form_field = serializers.IntegerField(required=True)

    repeat_group_key = serializers.UUIDField(
        required=False,
        allow_null=True
    )

    repeat_index = serializers.IntegerField(
        required=False,
        default=0
    )

    value = serializers.JSONField(
        required=False,
        allow_null=True
    )

    verification_status = serializers.CharField(
        required=False,
        allow_blank=True
    )
    
class ProjectScopeInputSerializer(serializers.Serializer):
    scope = serializers.IntegerField(required=True)

    activity_summary = serializers.CharField(
        required=False,
        allow_blank=True
    )

    verification_status = serializers.CharField(
        required=False,
        allow_blank=True
    )

    status = serializers.CharField(
        required=False,
        allow_blank=True
    )

    scope_responses = ScopeResponseInputSerializer(
        many=True,
        required=False
    )

class ProjectRecordInputSerializer(serializers.Serializer):

    project_name = serializers.CharField(required=True)

    employer_organization = serializers.CharField(
        required=False,
        allow_blank=True
    )

    client_organization = serializers.CharField(
        required=False,
        allow_blank=True
    )

    client_name_snapshot = serializers.CharField(
        required=False,
        allow_blank=True
    )

    client_visibility = serializers.CharField(
        required=False,
        allow_blank=True
    )

    country_code = serializers.CharField(
        required=False,
        allow_blank=True
    )

    city = serializers.CharField(
        required=False,
        allow_blank=True
    )

    role_title = serializers.IntegerField(
        required=False,
        allow_null=True
    )

    start_date = serializers.DateField(
        required=False
    )

    end_date = serializers.DateField(
        required=False,
        allow_null=True
    )

    is_current = serializers.BooleanField(
        required=False,
        default=False
    )

    allocation_percent = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False
    )

    is_primary_assignment = serializers.BooleanField(
        required=False,
        default=False
    )

    working_arrangement = serializers.CharField(
        required=False,
        allow_blank=True
    )

    engagement_explanation = serializers.CharField(
        required=False,
        allow_blank=True
    )

    declared_field_days = serializers.IntegerField(
        required=False,
        allow_null=True
    )

    responsibilities = serializers.CharField(
        required=False,
        allow_blank=True
    )

    achievements = serializers.CharField(
        required=False,
        allow_blank=True
    )

    verification_status = serializers.CharField(
        required=False,
        allow_blank=True
    )

    status = serializers.CharField(
        required=False,
        allow_blank=True
    )

    Experience_classification = serializers.CharField(
        required=False,
        allow_blank=True
    )

    industry_classification = serializers.IntegerField(
        required=False,
        allow_null=True
    )

    project_scopes = ProjectScopeInputSerializer(
        many=True,
        required=False
    )

class BulkProjectRecordSerializer(serializers.Serializer):
    professional = serializers.IntegerField(required=True)    
    project_records = serializers.ListField(
        child=ProjectRecordInputSerializer(), required=True
    )

    def validate(self, attrs):
        tenant = self.context.get("tenant")
        professional = self.context.get("professional")
        if not tenant:
            raise serializers.ValidationError({"tenant": "Tenant context is required."})
        
        return attrs

    def create(self, validated_data):
        tenant = self.context.get("tenant")
        professional = self.context["professional"]
        created_by = self.context.get("created_by")
        if not created_by and professional:
            created_by = getattr(professional, "user", None)
        if not created_by and tenant:
            created_by = getattr(tenant, "created_by", None)
        created_records = []

        with transaction.atomic():
            for project_payload in validated_data.get("project_records", []):
                client_name = project_payload.get("client_name_snapshot") or project_payload.get("client") or ""
                project = ProjectRecord.objects.create(
                    tenant=tenant,
                    professional=professional,

                    project_name=project_payload["project_name"],

                    employer_organization=project_payload.get("employer_organization"),
                    client_organization=project_payload.get("client_organization"),

                    client_name_snapshot=project_payload.get(
                        "client_name_snapshot"
                    ),

                    client_visibility=project_payload.get(
                        "client_visibility"
                    ),

                    country_code=project_payload.get(
                        "country_code"
                    ),

                    city=project_payload.get(
                        "city"
                    ),

                    role_title_id=project_payload.get(
                        "role_title"
                    ),

                    start_date=project_payload.get(
                        "start_date"
                    ),

                    end_date=project_payload.get(
                        "end_date"
                    ),

                    is_current=project_payload.get(
                        "is_current",
                        False
                    ),

                    allocation_percent=project_payload.get(
                        "allocation_percent"
                    ),

                    is_primary_assignment=project_payload.get(
                        "is_primary_assignment",
                        False
                    ),

                    working_arrangement=project_payload.get(
                        "working_arrangement"
                    ),

                    engagement_explanation=project_payload.get(
                        "engagement_explanation"
                    ),

                    declared_field_days=project_payload.get(
                        "declared_field_days"
                    ),

                    responsibilities=project_payload.get(
                        "responsibilities"
                    ),

                    achievements=project_payload.get(
                        "achievements"
                    ),

                    verification_status=project_payload.get(
                        "verification_status"
                    ),

                    status=project_payload.get(
                        "status",
                        CompletionStatus.DRAFT
                    ),

                    Experience_classification=project_payload.get(
                        "Experience_classification"
                    ),

                    industry_classification_id=project_payload.get(
                        "industry_classification"
                    ),
                )

                for scope_payload in project_payload.get("project_scopes", []):
                    scope_catalog = self._resolve_scope(scope_payload)                    
                    project_scope = ProjectScope.objects.create(
                        tenant=tenant,
                        project=project,

                        scope_id=scope_payload["scope"],

                        activity_summary=scope_payload.get(
                            "activity_summary"
                        ),

                        verification_status=scope_payload.get(
                            "verification_status"
                        ),

                        status=scope_payload.get(
                            "status",
                            CompletionStatus.DRAFT
                        ),
                    )

                    for response_payload in scope_payload.get("scope_responses", []):
                        form_field = self._resolve_form_field(response_payload)
                        ScopeResponse.objects.create(
                            tenant=tenant,

                            project_scope=project_scope,

                            form_field_id=response_payload["form_field"],

                            repeat_group_key=response_payload.get(
                                "repeat_group_key"
                            ),

                            repeat_index=response_payload.get(
                                "repeat_index",
                                0
                            ),

                            value=response_payload.get("value"),

                            verification_status=response_payload.get(
                                "verification_status"
                            ),
                        )

                created_records.append(project)

        return created_records

    # def _resolve_scope(self, scope_payload):
    #     scope_ref = (
    #         scope_payload.get("scope")
    #         or scope_payload.get("scope_code")
    #         or scope_payload.get("scope_name")
    #     )
    #     if not scope_ref:
    #         raise serializers.ValidationError(
    #             {"project_scopes": "Each scope entry must include scope_name, scope_code or scope."}
    #         )

    #     scope_catalog = ScopeCatalog.objects.filter(is_active=True).filter(
    #         models.Q(scope_name__iexact=scope_ref) | models.Q(code__iexact=scope_ref)
    #     ).first()
    #     if not scope_catalog:
    #         raise serializers.ValidationError(
    #             {"project_scopes": f"Scope '{scope_ref}' was not found."}
    #         )
    #     return scope_catalog

    def _resolve_scope(self, scope_payload):

        scope_id = scope_payload.get("scope")

        if scope_id:
            scope_catalog = ScopeCatalog.objects.filter(
                pk=scope_id,
                is_active=True
            ).first()

            if not scope_catalog:
                raise serializers.ValidationError(
                    {"project_scopes": f"Scope id '{scope_id}' was not found."}
                )

            return scope_catalog

        scope_code = scope_payload.get("scope_code")
        if scope_code:
            scope_catalog = ScopeCatalog.objects.filter(
                code__iexact=scope_code,
                is_active=True
            ).first()

            if not scope_catalog:
                raise serializers.ValidationError(
                    {"project_scopes": f"Scope code '{scope_code}' was not found."}
                )

            return scope_catalog

        scope_name = scope_payload.get("scope_name")
        if scope_name:
            scope_catalog = ScopeCatalog.objects.filter(
                scope_name__iexact=scope_name,
                is_active=True
            ).first()

            if not scope_catalog:
                raise serializers.ValidationError(
                    {"project_scopes": f"Scope name '{scope_name}' was not found."}
                )

            return scope_catalog

        raise serializers.ValidationError(
            {
                "project_scopes":
                "Each scope entry must include scope, scope_code or scope_name."
            }
        )
    def _resolve_form_field(self, response_payload):
        field_id = response_payload.get("form_field")

        field = FormField.objects.filter(pk=field_id).first()

        if not field:
            raise serializers.ValidationError(
                {"scope_responses": f"FormField '{field_id}' was not found."}
            )

        return field

    


class ProjectScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectScope
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )







class ScopeResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScopeResponse
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )



class ExposureLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExposureLog
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )





class ProfessionalAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalAssignment
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )