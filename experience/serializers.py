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
    field_code = serializers.CharField(required=True)
    value = serializers.JSONField(required=False, allow_null=True)


class ProjectScopeInputSerializer(serializers.Serializer):
    scope_name = serializers.CharField(required=False, allow_blank=False)
    scope_code = serializers.CharField(required=False, allow_blank=False)
    scope = serializers.CharField(required=False, allow_blank=False)
    authority_action = serializers.CharField(required=False, allow_blank=True)
    scope_responses = serializers.ListField(
        child=ScopeResponseInputSerializer(), required=False, default=list
    )


class ProjectRecordInputSerializer(serializers.Serializer):
    project_name = serializers.CharField(required=True)
    client = serializers.CharField(required=False, allow_blank=True, write_only=True)
    client_name_snapshot = serializers.CharField(required=False, allow_blank=True)
    start_date = serializers.DateField(required=False, default=date.today)
    end_date = serializers.DateField(required=False, allow_null=True)
    is_current = serializers.BooleanField(required=False, default=False)
    project_scopes = serializers.ListField(
        child=ProjectScopeInputSerializer(), required=False, default=list
    )


class BulkProjectRecordSerializer(serializers.Serializer):
    professional_profile = serializers.UUIDField(required=True)
    project_records = serializers.ListField(
        child=ProjectRecordInputSerializer(), required=True
    )

    def validate(self, attrs):
        tenant = self.context.get("tenant")
        professional = self.context.get("professional")
        if not tenant:
            raise serializers.ValidationError({"tenant": "Tenant context is required."})
        if not professional:
            raise serializers.ValidationError(
                {"professional": "Professional context is required."}
            )
        return attrs

    def create(self, validated_data):
        tenant = self.context.get("tenant")
        professional = self.context.get("professional")
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
                    client_name_snapshot=client_name,
                    start_date=project_payload.get("start_date", date.today()),
                    end_date=project_payload.get("end_date"),
                    is_current=project_payload.get("is_current", False),
                    status=CompletionStatus.DRAFT,
                )

                for scope_payload in project_payload.get("project_scopes", []):
                    scope_catalog = self._resolve_scope(scope_payload)
                    authority_action = self._resolve_authority_action(scope_payload, created_by)
                    project_scope = ProjectScope.objects.create(
                        tenant=tenant,
                        project=project,
                        scope=scope_catalog,
                        authority_action=authority_action,
                        status=CompletionStatus.DRAFT,
                    )

                    for response_payload in scope_payload.get("scope_responses", []):
                        form_field = self._resolve_form_field(response_payload)
                        ScopeResponse.objects.create(
                            tenant=tenant,
                            project_scope=project_scope,
                            form_field=form_field,
                            value=response_payload.get("value"),
                        )

                created_records.append(project)

        return created_records

    def _resolve_scope(self, scope_payload):
        scope_ref = (
            scope_payload.get("scope")
            or scope_payload.get("scope_code")
            or scope_payload.get("scope_name")
        )
        if not scope_ref:
            raise serializers.ValidationError(
                {"project_scopes": "Each scope entry must include scope_name, scope_code or scope."}
            )

        scope_catalog = ScopeCatalog.objects.filter(is_active=True).filter(
            models.Q(scope_name__iexact=scope_ref) | models.Q(code__iexact=scope_ref)
        ).first()
        if not scope_catalog:
            raise serializers.ValidationError(
                {"project_scopes": f"Scope '{scope_ref}' was not found."}
            )
        return scope_catalog

    def _resolve_form_field(self, response_payload):
        field_code = response_payload.get("field_code")
        if not field_code:
            raise serializers.ValidationError(
                {"scope_responses": "Each scope response must include field_code."}
            )

        field = FormField.objects.filter(field_code__iexact=field_code).first()
        if not field:
            raise serializers.ValidationError(
                {"scope_responses": f"Form field '{field_code}' was not found."}
            )
        return field

    def _resolve_authority_action(self, scope_payload, created_by):
        authority_action = scope_payload.get("authority_action")
        if authority_action:
            reference_value = ReferenceValue.objects.filter(
                models.Q(code__iexact=authority_action)
                | models.Q(label__iexact=authority_action)
            ).filter(option_set__option_type__iexact="AUTHORITY_ACTION").first()
            if reference_value:
                return reference_value

        option_set, _ = ReferencevalueoptionSet.objects.get_or_create(option_type="AUTHORITY_ACTION")
        reference_value, _ = ReferenceValue.objects.get_or_create(
            option_set=option_set,
            code="PERFORMED",
            defaults={"label": "Performed", "created_by": created_by},
        )
        return reference_value


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