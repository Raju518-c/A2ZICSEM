from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import *
from .serializers import *
from datetime import timedelta
from decimal import Decimal
from collections import defaultdict
from datetime import date
from django.db import transaction
from django.db.models import Prefetch
from django.utils import timezone

from professionals.models import *
from experience.models import *
from competency.models import *
from catalog.models import *
from .governance_calculation_engine import *
import uuid
from datetime import date, datetime


from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction

from rest_framework import serializers, status

from accounts.models import UserTbl
from competency.models import ProfessionalScope
from evidence.models import EvidenceDocument
from experience.models import ProjectRecord
from professionals.models import (
    CredentialRecord,
    ProfessionalProfile,
    ProfessionalReview,
)

from governance.models import (
    CalculatedFieldCode,
    CalculatedFieldOverride,
    CalculatedFieldValueHistory,
)

from governance.serializers import CalculatedFieldAdminVerificationSerializer



@method_decorator(csrf_exempt, name='dispatch')
class AuditEventListCreateAPIView(APIView):
    """
    GET  : Get all audit events
    POST : Create a new audit event
    """
    permission_classes = [AllowAny]
   
    def get(self, request):
        audit_events = AuditEvent.objects.all().order_by("-occurred_at")

        serializer = AuditEventSerializer(
            audit_events,
            many=True,
        )

        return Response(
            {
                "success": True,
                "message": "Audit events fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=AuditEventSerializer)
    def post(self, request):
        serializer = AuditEventSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Audit event created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@method_decorator(csrf_exempt, name='dispatch')
class AuditEventRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Retrieve audit event by ID
    PUT    : Update audit event
    DELETE : Delete audit event
    """
    permission_classes = [AllowAny]
   
    def get_object(self, pk):
        try:
            return AuditEvent.objects.get(pk=pk)
        except AuditEvent.DoesNotExist:
            return None

    def get(self, request, pk):
        audit_event = self.get_object(pk)

        if not audit_event:
            return Response(
                {
                    "success": False,
                    "message": "Audit event not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AuditEventSerializer(audit_event)

        return Response(
            {
                "success": True,
                "message": "Audit event retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=AuditEventSerializer)
    def put(self, request, pk):
        audit_event = self.get_object(pk)

        if not audit_event:
            return Response(
                {
                    "success": False,
                    "message": "Audit event not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AuditEventSerializer(
            audit_event,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Audit event updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        audit_event = self.get_object(pk)

        if not audit_event:
            return Response(
                {
                    "success": False,
                    "message": "Audit event not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        audit_event.delete()

        return Response(
            {
                "success": True,
                "message": "Audit event deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class CalculatedFieldOverrideListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = CalculatedFieldOverride.objects.all().order_by("-created_at")

        serializer = CalculatedFieldOverrideSerializer(
            queryset,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": "Calculated field overrides fetched successfully.",
                "data": serializer.data,
            }
        )

    @extend_schema(request=CalculatedFieldOverrideSerializer)
    def post(self, request):
        serializer = CalculatedFieldOverrideSerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Calculated field override created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@method_decorator(csrf_exempt, name="dispatch")
class CalculatedFieldOverrideRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return CalculatedFieldOverride.objects.get(pk=pk)
        except CalculatedFieldOverride.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)

        if not obj:
            return Response(
                {
                    "success": False,
                    "message": "Calculated field override not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CalculatedFieldOverrideSerializer(obj)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            }
        )

    @extend_schema(request=CalculatedFieldOverrideSerializer)
    def put(self, request, pk):
        obj = self.get_object(pk)

        if not obj:
            return Response(
                {
                    "success": False,
                    "message": "Calculated field override not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CalculatedFieldOverrideSerializer(
            obj,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Updated successfully.",
                    "data": serializer.data,
                }
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        obj = self.get_object(pk)

        if not obj:
            return Response(
                {
                    "success": False,
                    "message": "Calculated field override not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        obj.delete()

        return Response(
            {
                "success": True,
                "message": "Deleted successfully.",
            }
        )



@method_decorator(csrf_exempt, name="dispatch")
class CalculatedFieldValueHistoryListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = CalculatedFieldValueHistory.objects.all().order_by("-created_at")

        serializer = CalculatedFieldValueHistorySerializer(
            queryset,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": "Calculated field overrides fetched successfully.",
                "data": serializer.data,
            }
        )

    @extend_schema(request=CalculatedFieldValueHistorySerializer)
    def post(self, request):
        serializer = CalculatedFieldValueHistorySerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Calculated field override created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@method_decorator(csrf_exempt, name="dispatch")
class CalculatedFieldValueHistoryRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return CalculatedFieldValueHistory.objects.get(pk=pk)
        except CalculatedFieldValueHistory.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)

        if not obj:
            return Response(
                {
                    "success": False,
                    "message": "Calculated field override not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CalculatedFieldValueHistorySerializer(obj)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            }
        )

    @extend_schema(request=CalculatedFieldValueHistorySerializer)
    def put(self, request, pk):
        obj = self.get_object(pk)

        if not obj:
            return Response(
                {
                    "success": False,
                    "message": "Calculated field override not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CalculatedFieldValueHistorySerializer(
            obj,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Updated successfully.",
                    "data": serializer.data,
                }
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        obj = self.get_object(pk)

        if not obj:
            return Response(
                {
                    "success": False,
                    "message": "Calculated field override not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        obj.delete()

        return Response(
            {
                "success": True,
                "message": "Deleted successfully.",
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class CalculationRuleSetListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = CalculationRuleSet.objects.all().order_by("-created_at")

        serializer = CalculationRuleSetSerializer(
            queryset,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": "Calculated field overrides fetched successfully.",
                "data": serializer.data,
            }
        )

    @extend_schema(request=CalculationRuleSetSerializer)
    def post(self, request):
        serializer = CalculationRuleSetSerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Calculated field override created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@method_decorator(csrf_exempt, name="dispatch")
class CalculationRuleSetRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return CalculationRuleSet.objects.get(pk=pk)
        except CalculationRuleSet.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)

        if not obj:
            return Response(
                {
                    "success": False,
                    "message": "Calculated field override not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CalculationRuleSetSerializer(obj)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            }
        )

    @extend_schema(request=CalculationRuleSetSerializer)
    def put(self, request, pk):
        obj = self.get_object(pk)

        if not obj:
            return Response(
                {
                    "success": False,
                    "message": "Calculated field override not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CalculationRuleSetSerializer(
            obj,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Updated successfully.",
                    "data": serializer.data,
                }
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        obj = self.get_object(pk)

        if not obj:
            return Response(
                {
                    "success": False,
                    "message": "Calculated field override not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        obj.delete()

        return Response(
            {
                "success": True,
                "message": "Deleted successfully.",
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class CalculationRuleListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = CalculationRule.objects.all().order_by("-created_at")

        serializer = CalculationRuleSerializer(
            queryset,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": "Calculated field overrides fetched successfully.",
                "data": serializer.data,
            }
        )

    @extend_schema(request=CalculationRuleSerializer)
    def post(self, request):
        serializer = CalculationRuleSerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Calculated field override created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@method_decorator(csrf_exempt, name="dispatch")
class CalculationRuleRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return CalculationRule.objects.get(pk=pk)
        except CalculationRule.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)

        if not obj:
            return Response(
                {
                    "success": False,
                    "message": "Calculated field override not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CalculationRuleSerializer(obj)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            }
        )

    @extend_schema(request=CalculationRuleSerializer)
    def put(self, request, pk):
        obj = self.get_object(pk)

        if not obj:
            return Response(
                {
                    "success": False,
                    "message": "Calculated field override not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CalculationRuleSerializer(
            obj,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Updated successfully.",
                    "data": serializer.data,
                }
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        obj = self.get_object(pk)

        if not obj:
            return Response(
                {
                    "success": False,
                    "message": "Calculated field override not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        obj.delete()

        return Response(
            {
                "success": True,
                "message": "Deleted successfully.",
            }
        )




"""governance/views.py additions — the two requested endpoints.

Add below the CalculatedFieldOverride/CalculatedFieldValueHistory/
CalculationRuleSet/CalculationRule CRUD views already built. Same style:
csrf_exempt + AllowAny, {success, message, data} envelope.
"""


# ============================================================
# 1. System decides the value and saves it into the respective table
# ============================================================


@method_decorator(csrf_exempt, name="dispatch")
class CalculateSystemFieldAPIView(APIView):
    """
    POST : Evaluate one of the 15 system-calculated fields for a
    professional (optionally scoped to one Industry/Scope) using the
    tenant's PUBLISHED admin rules, then write the concluded value into
    the actual field on the main/related table and append a
    CalculatedFieldValueHistory row (change_source=SYSTEM_RECALCULATION).

    Body:
      {
        "professional": <id>,
        "calculation_field_code": "QUALION_LEVEL",
        "scope": <id>   // required for scoped fields: CALENDAR_EXPERIENCE,
                        // VERIFIED_FIELD_DAYS, QUALION_LEVEL, DEPLOYABILITY_FLAG
      }
    """

    permission_classes = [AllowAny]

    @extend_schema(request=None)
    def post(self, request):
        professional_id = request.data.get("professional")
        calculation_field_code = request.data.get("calculation_field_code")
        scope_id = request.data.get("scope")

        if not professional_id or not calculation_field_code:
            return Response(
                {
                    "success": False,
                    "message": "'professional' and 'calculation_field_code' are required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if calculation_field_code not in FIELD_HANDLERS:
            supported = ", ".join(sorted(FIELD_HANDLERS.keys()))
            return Response(
                {
                    "success": False,
                    "message": (
                        f"'{calculation_field_code}' is not yet runnable — its destination "
                        f"field doesn't exist on the model yet. Supported fields: {supported}."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            professional = ProfessionalProfile.objects.get(pk=professional_id)
        except ProfessionalProfile.DoesNotExist:
            return Response(
                {"success": False, "message": "Professional not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        scope = None
        if calculation_field_code in SCOPED_FIELDS:
            if not scope_id:
                return Response(
                    {
                        "success": False,
                        "message": f"'scope' is required for {calculation_field_code}.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                scope = ScopeCatalog.objects.get(pk=scope_id)
            except ScopeCatalog.DoesNotExist:
                return Response(
                    {"success": False, "message": "Scope not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        try:
            result = FIELD_HANDLERS[calculation_field_code](professional, scope, professional.tenant)
            previous_raw, history = apply_calculated_value(
                tenant=professional.tenant,
                professional=professional,
                target_instance=result["target_instance"],
                field_name=result["field_name"],
                calculation_field_code=calculation_field_code,
                resolved_value=result["resolved_value"],
                new_value_raw=result["new_value_raw"],
                ruleset_version=result["ruleset_version"],
                change_source="SYSTEM_RECALCULATION",
            )
        except CalculationError as exc:
            return Response(
                {"success": False, "message": str(exc)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return Response(
            {
                "success": True,
                "message": "System calculated field evaluated and saved successfully.",
                "data": {
                    "calculation_field_code": calculation_field_code,
                    "professional": professional.pk,
                    "scope": scope.pk if scope else None,
                    "field_name": result["field_name"],
                    "previous_value": previous_raw,
                    "new_value": result["new_value_raw"],
                    "rule_applied": result["rule_label"],
                    "ruleset_version": result["ruleset_version"],
                    "history_id": history.pk,
                },
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# 2. Admin override — creates the override record and, if approved in
#    the same call, writes the field + logs history immediately
# ============================================================







# =============================================================================
# CALCULATED FIELD → ACTUAL MODEL FIELD MAPPING
# =============================================================================

SCOPE_FIELD_MAP = {
    CalculatedFieldCode.CALENDAR_EXPERIENCE: "calendar_experience_months",
    CalculatedFieldCode.VERIFIED_FIELD_DAYS: "verified_field_days",
    CalculatedFieldCode.VERIFIED_PROJECT_COUNT: "verified_project_count",
    CalculatedFieldCode.HIGHEST_AUTHORITY_REACHED: "highest_authority_reached",
    CalculatedFieldCode.QUALION_LEVEL: "current_qualion_level",
    CalculatedFieldCode.DEPLOYABILITY_FLAG: "is_deployable",
}


PROFILE_FIELD_MAP = {
    CalculatedFieldCode.PROFESSIONAL_HEADLINE: "headline",
    CalculatedFieldCode.PRIMARY_ROLE: "primary_role",
    CalculatedFieldCode.ADDITIONAL_ROLES: "additional_roles",
    CalculatedFieldCode.INDUSTRIES_SERVED: "industries_served",
    CalculatedFieldCode.TOTAL_CAREER_EXPERIENCE: "total_career_experience_months",
}


# =============================================================================
# JSON SAFE VALUE
# =============================================================================

def json_safe_value(value):
    """
    Converts DB/model values into values safe to store inside JSONField.
    """

    if value is None:
        return None

    if isinstance(value, models.Model):
        return {
            "id": value.pk,
            "display": str(value),
        }

    if isinstance(value, Decimal):
        return str(value)

    if isinstance(value, (date, datetime)):
        return value.isoformat()

    if isinstance(value, uuid.UUID):
        return str(value)

    if isinstance(value, dict):
        return {
            key: json_safe_value(val)
            for key, val in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            json_safe_value(item)
            for item in value
        ]

    return value


# =============================================================================
# READ CURRENT FIELD VALUE
# =============================================================================

def get_field_snapshot(instance, field_name):
    """
    Reads the current value before admin override.

    Supports:
    - normal fields
    - ForeignKey
    - ManyToMany
    """

    field = instance._meta.get_field(field_name)

    if field.many_to_many:
        return [
            json_safe_value(obj)
            for obj in getattr(instance, field_name).all()
        ]

    value = getattr(instance, field_name)

    return json_safe_value(value)


# =============================================================================
# RESOLVE FOREIGN KEY
# =============================================================================

def resolve_related_object(field, incoming_value):
    """
    Allows FK payload like:

        "value": 7

    or:

        "value": {
            "id": 7
        }

    or:

        "value": {
            "code": "L2"
        }
    """

    if incoming_value is None:
        return None

    related_model = field.related_model

    if isinstance(incoming_value, dict):

        related_id = incoming_value.get("id")

        if related_id is not None:
            try:
                return related_model.objects.get(
                    pk=related_id
                )
            except related_model.DoesNotExist:
                raise serializers.ValidationError({
                    "value": (
                        f"{related_model.__name__} "
                        f"with id={related_id} not found."
                    )
                })

        code = incoming_value.get("code")

        if code:
            try:
                return related_model.objects.get(
                    code=code
                )
            except related_model.DoesNotExist:
                raise serializers.ValidationError({
                    "value": (
                        f"{related_model.__name__} "
                        f"with code={code} not found."
                    )
                })

        raise serializers.ValidationError({
            "value": (
                "Related field value must contain "
                "'id' or 'code'."
            )
        })

    try:
        return related_model.objects.get(
            pk=incoming_value
        )
    except related_model.DoesNotExist:
        raise serializers.ValidationError({
            "value": (
                f"{related_model.__name__} "
                f"with id={incoming_value} not found."
            )
        })


# =============================================================================
# RESOLVE MANY TO MANY
# =============================================================================

def resolve_many_to_many_values(field, incoming_value):
    if incoming_value is None:
        return []

    if not isinstance(incoming_value, list):
        raise serializers.ValidationError({
            "value": f"{field.name} expects a list."
        })

    result = []

    for item in incoming_value:
        result.append(
            resolve_related_object(
                field,
                item,
            )
        )

    return result


# =============================================================================
# RESOLVE NORMAL FIELD
# =============================================================================

def resolve_normal_field_value(field, incoming_value):
    if incoming_value is None:
        return None

    try:
        resolved_value = field.to_python(
            incoming_value
        )
    except Exception as exc:
        raise serializers.ValidationError({
            "value": (
                f"Invalid value for {field.name}: "
                f"{str(exc)}"
            )
        })

    if field.choices:
        allowed_values = [
            choice[0]
            for choice in field.choices
        ]

        if resolved_value not in allowed_values:
            raise serializers.ValidationError({
                "value": (
                    f"Invalid value '{resolved_value}' "
                    f"for {field.name}. "
                    f"Allowed values: {allowed_values}"
                )
            })

    return resolved_value


# =============================================================================
# RESOLVE ANY MODEL FIELD VALUE
# =============================================================================

def resolve_new_field_value(instance, field_name, incoming_value):
    field = instance._meta.get_field(field_name)

    if field.many_to_many:
        return resolve_many_to_many_values(
            field,
            incoming_value,
        )

    if field.is_relation:
        return resolve_related_object(
            field,
            incoming_value,
        )

    return resolve_normal_field_value(
        field,
        incoming_value,
    )


# =============================================================================
# CONVERT RESOLVED VALUE FOR HISTORY / OVERRIDE JSON
# =============================================================================

def resolved_value_to_json(resolved_value):
    if isinstance(resolved_value, list):
        return [
            json_safe_value(item)
            for item in resolved_value
        ]

    return json_safe_value(
        resolved_value
    )


# =============================================================================
# APPLY ACTUAL FIELD VALUE
# =============================================================================

def apply_field_value(instance, field_name, resolved_value):
    """
    Updates actual corresponding table record.
    """

    field = instance._meta.get_field(field_name)

    if field.many_to_many:
        getattr(instance, field_name).set(
            resolved_value
        )
        return

    setattr(
        instance,
        field_name,
        resolved_value,
    )

    instance.save(
        update_fields=[field_name]
    )


# =============================================================================
# VALIDATE OVERRIDE REASON
# =============================================================================

def require_override_reason(item):
    """
    Reason is required only if actual value is being changed.
    """

    reason_code = item.get("reason_code")
    reason = item.get("reason", "").strip()

    if not reason_code:
        raise serializers.ValidationError({
            "reason_code": (
                f"reason_code is required because "
                f"{item['calculation_field_code']} "
                f"is being changed."
            )
        })

    if not reason:
        raise serializers.ValidationError({
            "reason": (
                f"reason is required because "
                f"{item['calculation_field_code']} "
                f"is being changed."
            )
        })

    return reason_code, reason


# =============================================================================
# GET EVIDENCE
# =============================================================================

def get_evidence(item):
    evidence_id = item.get("evidence_id")

    if not evidence_id:
        return None

    try:
        return EvidenceDocument.objects.get(
            pk=evidence_id
        )
    except EvidenceDocument.DoesNotExist:
        raise serializers.ValidationError({
            "evidence_id": (
                f"EvidenceDocument {evidence_id} "
                f"not found."
            )
        })


# =============================================================================
# CREATE OR UPDATE CURRENT OVERRIDE + ALWAYS CREATE HISTORY
# =============================================================================

def create_or_update_override_and_history(
    *,
    batch_id,
    professional,
    professional_scope,
    target_instance,
    field_name,
    calculation_field_code,
    previous_value,
    new_value,
    item,
    updated_by,
    ruleset_version,
):
    """
    CalculatedFieldOverride:
        One current/latest record per:
            professional
            + calculation_field_code
            + target model
            + target object

        First override:
            CREATE

        Future override of same field:
            UPDATE SAME ROW

    CalculatedFieldValueHistory:
        ALWAYS CREATE A NEW ROW.

    Example:

        first:
            250 -> 300

        second:
            300 -> 350

    Override:
        one row, latest value = 350

    History:
        row1 = 250 -> 300
        row2 = 300 -> 350
    """

    now = timezone.now()

    reason_code, reason = require_override_reason(
        item
    )

    evidence = get_evidence(
        item
    )

    content_type = ContentType.objects.get_for_model(
        target_instance.__class__
    )

    # -------------------------------------------------------------------------
    # Search existing CURRENT override record.
    # -------------------------------------------------------------------------

    override = CalculatedFieldOverride.objects.select_for_update().filter(
        professional=professional,
        calculation_field_code=calculation_field_code,
        content_type=content_type,
        object_id=target_instance.pk,
    ).first()

    # -------------------------------------------------------------------------
    # EXISTING OVERRIDE → UPDATE SAME ROW
    # -------------------------------------------------------------------------

    if override:

        override.batch_id = batch_id

        override.professional_scope = professional_scope

        override.field_name = field_name

        # IMPORTANT:
        #
        # Do NOT update:
        #
        # override.system_calculated_value
        #
        # It remains the ORIGINAL system value before
        # the first admin override.

        override.proposed_value = new_value

        override.override_reason_code = reason_code

        override.rationale = reason

        override.evidence = evidence

        override.request_type = (
            CalculatedFieldOverride.RequestType.CORRECTION
        )

        override.requested_by = updated_by

        override.requested_at = now

        override.reviewed_by = updated_by

        override.review_notes = reason

        override.reviewed_at = now

        override.decision = (
            CalculatedFieldOverride.Decision.APPROVED
        )

        override.final_approved_value = new_value

        override.approved_by = updated_by

        override.decision_reason = reason

        override.approved_at = now

        override.effective_from = now.date()

        if ruleset_version:
            override.system_ruleset_version = (
                ruleset_version
            )

        override.save()

        override_action = "UPDATED"

    # -------------------------------------------------------------------------
    # FIRST OVERRIDE → CREATE NEW CURRENT OVERRIDE ROW
    # -------------------------------------------------------------------------

    else:

        override = CalculatedFieldOverride.objects.create(
            tenant=professional.tenant,

            batch_id=batch_id,

            professional=professional,

            professional_scope=professional_scope,

            content_type=content_type,

            object_id=target_instance.pk,

            field_name=field_name,

            calculation_field_code=calculation_field_code,

            request_type=(
                CalculatedFieldOverride.RequestType.CORRECTION
            ),

            # Original system/current value before first override.
            system_calculated_value=previous_value,

            system_calculated_at=now,

            system_ruleset_version=ruleset_version,

            proposed_value=new_value,

            override_reason_code=reason_code,

            rationale=reason,

            evidence=evidence,

            requested_by=updated_by,

            requested_at=now,

            reviewed_by=updated_by,

            review_notes=reason,

            reviewed_at=now,

            decision=(
                CalculatedFieldOverride.Decision.APPROVED
            ),

            final_approved_value=new_value,

            approved_by=updated_by,

            decision_reason=reason,

            approved_at=now,

            effective_from=now.date(),
        )

        override_action = "CREATED"

    # -------------------------------------------------------------------------
    # HISTORY → ALWAYS CREATE NEW ROW
    # -------------------------------------------------------------------------

    history = CalculatedFieldValueHistory.objects.create(
        tenant=professional.tenant,

        batch_id=batch_id,

        professional=professional,

        professional_scope=professional_scope,

        content_type=content_type,

        object_id=target_instance.pk,

        field_name=field_name,

        calculation_field_code=calculation_field_code,

        # Immediate value before this particular update.
        previous_value=previous_value,

        new_value=new_value,

        reason_code=reason_code,

        reason=reason,

        change_source=(
            CalculatedFieldValueHistory.ChangeSource.OVERRIDE_APPROVED
        ),

        override=override,

        changed_by=updated_by,

        effective_from=now.date(),

        recalculation_ruleset_version=ruleset_version,
    )

    return override, history, override_action


# =============================================================================
# PROFESSIONAL SCOPE CALCULATED FIELDS
# =============================================================================

def process_scope_field(
    *,
    batch_id,
    professional,
    updated_by,
    item,
    ruleset_version,
):
    code = item["calculation_field_code"]

    professional_scope_id = item.get(
        "professional_scope_id"
    )

    try:
        professional_scope = (
            ProfessionalScope.objects
            .select_for_update()
            .get(
                pk=professional_scope_id,
                professional=professional,
            )
        )

    except ProfessionalScope.DoesNotExist:
        raise serializers.ValidationError({
            "professional_scope_id": (
                f"ProfessionalScope "
                f"{professional_scope_id} "
                f"does not belong to professional "
                f"{professional.pk}."
            )
        })

    field_name = SCOPE_FIELD_MAP[
        code
    ]

    # CURRENT actual value before admin update.
    previous_value = get_field_snapshot(
        professional_scope,
        field_name,
    )

    try:
        resolved_value = resolve_new_field_value(
            professional_scope,
            field_name,
            item["value"],
        )

    except serializers.ValidationError:
        raise

    except Exception as exc:
        raise serializers.ValidationError({
            "value": (
                f"Unable to resolve "
                f"{code}: {str(exc)}"
            )
        })

    new_value = resolved_value_to_json(
        resolved_value
    )

    # No actual change.
    if previous_value == new_value:
        return {
            "status": "SKIPPED",
            "calculation_field_code": code,
            "professional_scope_id": professional_scope.pk,
            "target_model": "ProfessionalScope",
            "target_id": professional_scope.pk,
            "field_name": field_name,
            "previous_value": previous_value,
            "new_value": new_value,
            "message": "Value unchanged.",
        }

    # Create/update override and create history BEFORE
    # changing actual target record.
    override, history, override_action = (
        create_or_update_override_and_history(
            batch_id=batch_id,
            professional=professional,
            professional_scope=professional_scope,
            target_instance=professional_scope,
            field_name=field_name,
            calculation_field_code=code,
            previous_value=previous_value,
            new_value=new_value,
            item=item,
            updated_by=updated_by,
            ruleset_version=ruleset_version,
        )
    )

    # Update actual ProfessionalScope field.
    apply_field_value(
        professional_scope,
        field_name,
        resolved_value,
    )

    return {
        "status": "UPDATED",
        "calculation_field_code": code,
        "professional_scope_id": professional_scope.pk,
        "target_model": "ProfessionalScope",
        "target_id": professional_scope.pk,
        "field_name": field_name,
        "previous_value": previous_value,
        "new_value": new_value,
        "override_id": str(override.pk),
        "override_action": override_action,
        "history_id": history.pk,
    }


# =============================================================================
# PROFESSIONAL PROFILE CALCULATED FIELDS
# =============================================================================

def process_profile_field(
    *,
    batch_id,
    professional,
    updated_by,
    item,
    ruleset_version,
):
    code = item["calculation_field_code"]

    profile = (
        ProfessionalProfile.objects
        .select_for_update()
        .get(
            pk=professional.pk
        )
    )

    field_name = PROFILE_FIELD_MAP[
        code
    ]

    previous_value = get_field_snapshot(
        profile,
        field_name,
    )

    try:
        resolved_value = resolve_new_field_value(
            profile,
            field_name,
            item["value"],
        )

    except serializers.ValidationError:
        raise

    except Exception as exc:
        raise serializers.ValidationError({
            "value": (
                f"Unable to resolve "
                f"{code}: {str(exc)}"
            )
        })

    new_value = resolved_value_to_json(
        resolved_value
    )

    if previous_value == new_value:
        return {
            "status": "SKIPPED",
            "calculation_field_code": code,
            "target_model": "ProfessionalProfile",
            "target_id": profile.pk,
            "field_name": field_name,
            "previous_value": previous_value,
            "new_value": new_value,
            "message": "Value unchanged.",
        }

    override, history, override_action = (
        create_or_update_override_and_history(
            batch_id=batch_id,
            professional=professional,
            professional_scope=None,
            target_instance=profile,
            field_name=field_name,
            calculation_field_code=code,
            previous_value=previous_value,
            new_value=new_value,
            item=item,
            updated_by=updated_by,
            ruleset_version=ruleset_version,
        )
    )

    apply_field_value(
        profile,
        field_name,
        resolved_value,
    )

    return {
        "status": "UPDATED",
        "calculation_field_code": code,
        "target_model": "ProfessionalProfile",
        "target_id": profile.pk,
        "field_name": field_name,
        "previous_value": previous_value,
        "new_value": new_value,
        "override_id": str(override.pk),
        "override_action": override_action,
        "history_id": history.pk,
    }


# =============================================================================
# PROFESSIONAL SUMMARY
# ProfessionalProfile.summary
# ProfessionalProfile.summary_source
# =============================================================================

def process_professional_summary(
    *,
    batch_id,
    professional,
    updated_by,
    item,
    ruleset_version,
):
    profile = (
        ProfessionalProfile.objects
        .select_for_update()
        .get(
            pk=professional.pk
        )
    )

    incoming = item["value"]

    previous_value = {
        "summary": profile.summary,
        "summary_source": profile.summary_source,
    }

    new_value = {
        "summary": incoming.get(
            "summary",
            profile.summary,
        ),

        "summary_source": incoming.get(
            "summary_source",
            profile.summary_source,
        ),
    }

    if previous_value == new_value:
        return {
            "status": "SKIPPED",
            "calculation_field_code": (
                CalculatedFieldCode.PROFESSIONAL_SUMMARY
            ),
            "target_model": "ProfessionalProfile",
            "target_id": profile.pk,
            "field_name": "summary,summary_source",
            "previous_value": previous_value,
            "new_value": new_value,
            "message": "Value unchanged.",
        }

    # Validate summary_source if it has choices.
    summary_source_field = (
        profile._meta.get_field(
            "summary_source"
        )
    )

    if summary_source_field.choices:
        allowed_values = [
            choice[0]
            for choice in summary_source_field.choices
        ]

        if new_value["summary_source"] not in allowed_values:
            raise serializers.ValidationError({
                "summary_source": (
                    f"Invalid summary_source "
                    f"'{new_value['summary_source']}'. "
                    f"Allowed values: {allowed_values}"
                )
            })

    override, history, override_action = (
        create_or_update_override_and_history(
            batch_id=batch_id,
            professional=professional,
            professional_scope=None,
            target_instance=profile,
            field_name="summary,summary_source",
            calculation_field_code=(
                CalculatedFieldCode.PROFESSIONAL_SUMMARY
            ),
            previous_value=previous_value,
            new_value=new_value,
            item=item,
            updated_by=updated_by,
            ruleset_version=ruleset_version,
        )
    )

    profile.summary = new_value[
        "summary"
    ]

    profile.summary_source = new_value[
        "summary_source"
    ]

    profile.save(
        update_fields=[
            "summary",
            "summary_source",
        ]
    )

    return {
        "status": "UPDATED",
        "calculation_field_code": (
            CalculatedFieldCode.PROFESSIONAL_SUMMARY
        ),
        "target_model": "ProfessionalProfile",
        "target_id": profile.pk,
        "field_name": "summary,summary_source",
        "previous_value": previous_value,
        "new_value": new_value,
        "override_id": str(override.pk),
        "override_action": override_action,
        "history_id": history.pk,
    }


# =============================================================================
# PROJECT RESPONSIBILITY BULLETS
# ProjectRecord.responsibilities
# =============================================================================

def process_project_responsibilities(
    *,
    batch_id,
    professional,
    updated_by,
    item,
    ruleset_version,
):
    project_record_id = item.get(
        "project_record_id"
    )

    try:
        project = (
            ProjectRecord.objects
            .select_for_update()
            .get(
                pk=project_record_id,
                professional=professional,
            )
        )

    except ProjectRecord.DoesNotExist:
        raise serializers.ValidationError({
            "project_record_id": (
                f"ProjectRecord "
                f"{project_record_id} "
                f"does not belong to professional "
                f"{professional.pk}."
            )
        })

    field_name = "responsibilities"

    previous_value = json_safe_value(
        project.responsibilities
    )

    field = project._meta.get_field(
        field_name
    )

    resolved_value = resolve_normal_field_value(
        field,
        item["value"],
    )

    new_value = json_safe_value(
        resolved_value
    )

    if previous_value == new_value:
        return {
            "status": "SKIPPED",
            "calculation_field_code": (
                CalculatedFieldCode.PROJECT_RESPONSIBILITY_BULLETS
            ),
            "project_record_id": project.pk,
            "target_model": "ProjectRecord",
            "target_id": project.pk,
            "field_name": field_name,
            "previous_value": previous_value,
            "new_value": new_value,
            "message": "Value unchanged.",
        }

    override, history, override_action = (
        create_or_update_override_and_history(
            batch_id=batch_id,
            professional=professional,
            professional_scope=None,
            target_instance=project,
            field_name=field_name,
            calculation_field_code=(
                CalculatedFieldCode.PROJECT_RESPONSIBILITY_BULLETS
            ),
            previous_value=previous_value,
            new_value=new_value,
            item=item,
            updated_by=updated_by,
            ruleset_version=ruleset_version,
        )
    )

    project.responsibilities = resolved_value

    project.save(
        update_fields=[
            "responsibilities"
        ]
    )

    return {
        "status": "UPDATED",
        "calculation_field_code": (
            CalculatedFieldCode.PROJECT_RESPONSIBILITY_BULLETS
        ),
        "project_record_id": project.pk,
        "target_model": "ProjectRecord",
        "target_id": project.pk,
        "field_name": field_name,
        "previous_value": previous_value,
        "new_value": new_value,
        "override_id": str(override.pk),
        "override_action": override_action,
        "history_id": history.pk,
    }


# =============================================================================
# CREDENTIAL STATUS
# CredentialRecord.status
# =============================================================================

def process_credential_status(
    *,
    batch_id,
    professional,
    updated_by,
    item,
    ruleset_version,
):
    credential_record_id = item.get(
        "credential_record_id"
    )

    try:
        credential = (
            CredentialRecord.objects
            .select_for_update()
            .get(
                pk=credential_record_id,
                professional=professional,
            )
        )

    except CredentialRecord.DoesNotExist:
        raise serializers.ValidationError({
            "credential_record_id": (
                f"CredentialRecord "
                f"{credential_record_id} "
                f"does not belong to professional "
                f"{professional.pk}."
            )
        })

    field_name = "status"

    previous_value = json_safe_value(
        credential.status
    )

    field = credential._meta.get_field(
        field_name
    )

    resolved_value = resolve_normal_field_value(
        field,
        item["value"],
    )

    new_value = json_safe_value(
        resolved_value
    )

    if previous_value == new_value:
        return {
            "status": "SKIPPED",
            "calculation_field_code": (
                CalculatedFieldCode.CREDENTIAL_STATUS
            ),
            "credential_record_id": credential.pk,
            "target_model": "CredentialRecord",
            "target_id": credential.pk,
            "field_name": field_name,
            "previous_value": previous_value,
            "new_value": new_value,
            "message": "Value unchanged.",
        }

    override, history, override_action = (
        create_or_update_override_and_history(
            batch_id=batch_id,
            professional=professional,
            professional_scope=None,
            target_instance=credential,
            field_name=field_name,
            calculation_field_code=(
                CalculatedFieldCode.CREDENTIAL_STATUS
            ),
            previous_value=previous_value,
            new_value=new_value,
            item=item,
            updated_by=updated_by,
            ruleset_version=ruleset_version,
        )
    )

    credential.status = resolved_value

    credential.save(
        update_fields=[
            "status"
        ]
    )

    return {
        "status": "UPDATED",
        "calculation_field_code": (
            CalculatedFieldCode.CREDENTIAL_STATUS
        ),
        "credential_record_id": credential.pk,
        "target_model": "CredentialRecord",
        "target_id": credential.pk,
        "field_name": field_name,
        "previous_value": previous_value,
        "new_value": new_value,
        "override_id": str(override.pk),
        "override_action": override_action,
        "history_id": history.pk,
    }


# =============================================================================
# CANDIDATE / MENTOR CLASSIFICATION
#
# ProfessionalProfile:
#   current_classification
#   classification_status
#
# ProfessionalReview:
#   system_recommendation
#   decision
#   final_classification
# =============================================================================

def process_candidate_mentor_classification(
    *,
    batch_id,
    professional,
    updated_by,
    item,
    ruleset_version,
):
    professional_review_id = item.get(
        "professional_review_id"
    )

    incoming = item["value"]

    if not isinstance(incoming, dict):
        raise serializers.ValidationError({
            "value": (
                "CANDIDATE_MENTOR_CLASSIFICATION "
                "value must be an object."
            )
        })

    profile = (
        ProfessionalProfile.objects
        .select_for_update()
        .get(
            pk=professional.pk
        )
    )

    try:
        review = (
            ProfessionalReview.objects
            .select_for_update()
            .get(
                pk=professional_review_id,
                professional=professional,
            )
        )

    except ProfessionalReview.DoesNotExist:
        raise serializers.ValidationError({
            "professional_review_id": (
                f"ProfessionalReview "
                f"{professional_review_id} "
                f"does not belong to professional "
                f"{professional.pk}."
            )
        })

    previous_value = {
        "current_classification": (
            json_safe_value(
                profile.current_classification
            )
        ),
        "classification_status": (
            json_safe_value(
                profile.classification_status
            )
        ),
        "system_recommendation": (
            json_safe_value(
                review.system_recommendation
            )
        ),
        "decision": (
            json_safe_value(
                review.decision
            )
        ),
        "final_classification": (
            json_safe_value(
                review.final_classification
            )
        ),
    }

    # -------------------------------------------------------------------------
    # Resolve each incoming field only if provided.
    # -------------------------------------------------------------------------

    if "current_classification" in incoming:
        current_classification = (
            resolve_new_field_value(
                profile,
                "current_classification",
                incoming["current_classification"],
            )
        )
    else:
        current_classification = (
            profile.current_classification
        )

    if "classification_status" in incoming:
        classification_status = (
            resolve_new_field_value(
                profile,
                "classification_status",
                incoming["classification_status"],
            )
        )
    else:
        classification_status = (
            profile.classification_status
        )

    if "system_recommendation" in incoming:
        system_recommendation = (
            resolve_new_field_value(
                review,
                "system_recommendation",
                incoming["system_recommendation"],
            )
        )
    else:
        system_recommendation = (
            review.system_recommendation
        )

    if "decision" in incoming:
        decision = (
            resolve_new_field_value(
                review,
                "decision",
                incoming["decision"],
            )
        )
    else:
        decision = review.decision

    if "final_classification" in incoming:
        final_classification = (
            resolve_new_field_value(
                review,
                "final_classification",
                incoming["final_classification"],
            )
        )
    else:
        final_classification = (
            review.final_classification
        )

    new_value = {
        "current_classification": (
            json_safe_value(
                current_classification
            )
        ),
        "classification_status": (
            json_safe_value(
                classification_status
            )
        ),
        "system_recommendation": (
            json_safe_value(
                system_recommendation
            )
        ),
        "decision": (
            json_safe_value(
                decision
            )
        ),
        "final_classification": (
            json_safe_value(
                final_classification
            )
        ),
    }

    if previous_value == new_value:
        return {
            "status": "SKIPPED",
            "calculation_field_code": (
                CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION
            ),
            "professional_review_id": review.pk,
            "target_model": (
                "ProfessionalProfile + ProfessionalReview"
            ),
            "previous_value": previous_value,
            "new_value": new_value,
            "message": "Value unchanged.",
        }

    override, history, override_action = (
        create_or_update_override_and_history(
            batch_id=batch_id,
            professional=professional,
            professional_scope=None,
            target_instance=profile,
            field_name=(
                "current_classification,"
                "classification_status,"
                "ProfessionalReview.system_recommendation,"
                "ProfessionalReview.decision,"
                "ProfessionalReview.final_classification"
            ),
            calculation_field_code=(
                CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION
            ),
            previous_value=previous_value,
            new_value=new_value,
            item=item,
            updated_by=updated_by,
            ruleset_version=ruleset_version,
        )
    )

    # -------------------------------------------------------------------------
    # Update ProfessionalProfile
    # -------------------------------------------------------------------------

    profile.current_classification = (
        current_classification
    )

    profile.classification_status = (
        classification_status
    )

    profile.save(
        update_fields=[
            "current_classification",
            "classification_status",
        ]
    )

    # -------------------------------------------------------------------------
    # Update ProfessionalReview
    # -------------------------------------------------------------------------

    review.system_recommendation = (
        system_recommendation
    )

    review.decision = decision

    review.final_classification = (
        final_classification
    )

    review.save(
        update_fields=[
            "system_recommendation",
            "decision",
            "final_classification",
        ]
    )

    return {
        "status": "UPDATED",
        "calculation_field_code": (
            CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION
        ),
        "target_model": (
            "ProfessionalProfile + ProfessionalReview"
        ),
        "target_id": profile.pk,
        "professional_review_id": review.pk,
        "previous_value": previous_value,
        "new_value": new_value,
        "override_id": str(override.pk),
        "override_action": override_action,
        "history_id": history.pk,
    }


# =============================================================================
# MAIN CALCULATED FIELD ROUTER
# =============================================================================

def process_calculated_field(
    *,
    batch_id,
    professional,
    updated_by,
    item,
    ruleset_version,
):
    code = item[
        "calculation_field_code"
    ]

    # -------------------------------------------------------------------------
    # ProfessionalScope fields
    # -------------------------------------------------------------------------

    if code in SCOPE_FIELD_MAP:
        return process_scope_field(
            batch_id=batch_id,
            professional=professional,
            updated_by=updated_by,
            item=item,
            ruleset_version=ruleset_version,
        )

    # -------------------------------------------------------------------------
    # ProfessionalProfile normal fields
    # -------------------------------------------------------------------------

    if code in PROFILE_FIELD_MAP:
        return process_profile_field(
            batch_id=batch_id,
            professional=professional,
            updated_by=updated_by,
            item=item,
            ruleset_version=ruleset_version,
        )

    # -------------------------------------------------------------------------
    # Professional summary
    # -------------------------------------------------------------------------

    if code == CalculatedFieldCode.PROFESSIONAL_SUMMARY:
        return process_professional_summary(
            batch_id=batch_id,
            professional=professional,
            updated_by=updated_by,
            item=item,
            ruleset_version=ruleset_version,
        )

    # -------------------------------------------------------------------------
    # Project responsibility
    # -------------------------------------------------------------------------

    if code == CalculatedFieldCode.PROJECT_RESPONSIBILITY_BULLETS:
        return process_project_responsibilities(
            batch_id=batch_id,
            professional=professional,
            updated_by=updated_by,
            item=item,
            ruleset_version=ruleset_version,
        )

    # -------------------------------------------------------------------------
    # Credential status
    # -------------------------------------------------------------------------

    if code == CalculatedFieldCode.CREDENTIAL_STATUS:
        return process_credential_status(
            batch_id=batch_id,
            professional=professional,
            updated_by=updated_by,
            item=item,
            ruleset_version=ruleset_version,
        )

    # -------------------------------------------------------------------------
    # Candidate / Mentor classification
    # -------------------------------------------------------------------------

    if code == CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION:
        return process_candidate_mentor_classification(
            batch_id=batch_id,
            professional=professional,
            updated_by=updated_by,
            item=item,
            ruleset_version=ruleset_version,
        )

    raise serializers.ValidationError({
        "calculation_field_code": (
            f"Unsupported calculated field code: "
            f"{code}."
        )
    })


# =============================================================================
# SINGLE + BULK ADMIN VERIFICATION API
# =============================================================================

@method_decorator(
    csrf_exempt,
    name="dispatch",
)
class CalculatedFieldAdminVerificationAPIView(APIView):
    """
    Handles BOTH:

    1 field:
        fields = [ {...} ]

    multiple fields:
        fields = [ {...}, {...}, {...} ]

    CalculatedFieldOverride:
        CREATE first time
        UPDATE same row next time

    CalculatedFieldValueHistory:
        ALWAYS CREATE NEW HISTORY ROW

    Actual target table:
        ALWAYS updated when value changes.
    """

    permission_classes = [
        AllowAny
    ]

    @extend_schema(
        request=CalculatedFieldAdminVerificationSerializer,

        responses={
            200: OpenApiResponse(
                description=(
                    "Calculated fields verified "
                    "successfully."
                )
            ),
            400: OpenApiResponse(
                description=(
                    "Invalid request or field update."
                )
            ),
            404: OpenApiResponse(
                description=(
                    "Professional or admin user "
                    "not found."
                )
            ),
        },

        examples=[
            OpenApiExample(
                "Bulk admin verification",
                value={
                    "professional_profile_id": 2,
                    "updated_by": 25,
                    "system_ruleset_version": "2026.1",
                    "fields": [
                        {
                            "calculation_field_code": "CALENDAR_EXPERIENCE",
                            "professional_scope_id": 10,
                            "value": 15,
                            "reason_code": "SOURCE_DATA_INCOMPLETE",
                            "reason": (
                                "Additional employment "
                                "documents verified."
                            ),
                        },
                        {
                            "calculation_field_code": "VERIFIED_FIELD_DAYS",
                            "professional_scope_id": 10,
                            "value": "300.00",
                            "reason_code": "SOURCE_DATA_INCOMPLETE",
                            "reason": (
                                "Additional site logs "
                                "were verified."
                            ),
                        },
                        {
                            "calculation_field_code": "QUALION_LEVEL",
                            "professional_scope_id": 10,
                            "value": 7,
                            "reason_code": "RULE_DOES_NOT_FIT_SITUATION",
                            "reason": (
                                "Admin verification supports "
                                "the revised Qualion level."
                            ),
                        },
                        {
                            "calculation_field_code": "PROFESSIONAL_HEADLINE",
                            "value": (
                                "Bridge & Heavy Structures "
                                "Professional | Infrastructure"
                            ),
                            "reason_code": "SOURCE_DATA_INCOMPLETE",
                            "reason": (
                                "Headline updated after "
                                "document verification."
                            ),
                        },
                    ],
                },
                request_only=True,
            ),
        ],

        tags=[
            "calculated-fields"
        ],

        summary=(
            "Admin verify calculated fields"
        ),

        description=(
            "Handles single or multiple calculated "
            "field overrides in one request."
        ),
    )
    def post(self, request):

        serializer = (
            CalculatedFieldAdminVerificationSerializer(
                data=request.data
            )
        )

        # ---------------------------------------------------------------------
        # Request validation
        # ---------------------------------------------------------------------

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data

        # ---------------------------------------------------------------------
        # Professional
        # ---------------------------------------------------------------------

        try:
            professional = (
                ProfessionalProfile.objects.get(
                    pk=data[
                        "professional_profile_id"
                    ]
                )
            )

        except ProfessionalProfile.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": (
                        "ProfessionalProfile "
                        "not found."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # ---------------------------------------------------------------------
        # Admin / updated_by
        # ---------------------------------------------------------------------

        try:
            updated_by = (
                UserTbl.objects.get(
                    pk=data["updated_by"]
                )
            )

        except UserTbl.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": (
                        "Updated-by user "
                        "not found."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # One batch for entire single/bulk submit.
        batch_id = uuid.uuid4()

        ruleset_version = data.get(
            "system_ruleset_version",
            "",
        )

        # ---------------------------------------------------------------------
        # Entire request is atomic.
        # ---------------------------------------------------------------------

        try:

            with transaction.atomic():

                results = []

                for index, item in enumerate(
                    data["fields"]
                ):

                    try:

                        result = (
                            process_calculated_field(
                                batch_id=batch_id,
                                professional=professional,
                                updated_by=updated_by,
                                item=item,
                                ruleset_version=ruleset_version,
                            )
                        )

                        result[
                            "request_index"
                        ] = index

                        results.append(
                            result
                        )

                    except serializers.ValidationError as exc:

                        # Add which array item failed.
                        raise serializers.ValidationError({
                            "field_index": index,
                            "calculation_field_code": (
                                item.get(
                                    "calculation_field_code"
                                )
                            ),
                            "errors": exc.detail,
                        })

        # ---------------------------------------------------------------------
        # Validation problem → transaction rollback.
        # ---------------------------------------------------------------------

        except serializers.ValidationError as exc:

            return Response(
                {
                    "success": False,
                    "message": (
                        "Calculated field verification "
                        "failed. No records were changed."
                    ),
                    "errors": exc.detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---------------------------------------------------------------------
        # Other unexpected problem → transaction rollback.
        # ---------------------------------------------------------------------

        except Exception as exc:

            return Response(
                {
                    "success": False,
                    "message": (
                        "Calculated field verification "
                        "failed. No records were changed."
                    ),
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ---------------------------------------------------------------------
        # Separate UPDATED / SKIPPED
        # ---------------------------------------------------------------------

        updated_results = [
            row
            for row in results
            if row["status"] == "UPDATED"
        ]

        skipped_results = [
            row
            for row in results
            if row["status"] == "SKIPPED"
        ]

        created_override_count = len([
            row
            for row in updated_results
            if row.get("override_action") == "CREATED"
        ])

        updated_override_count = len([
            row
            for row in updated_results
            if row.get("override_action") == "UPDATED"
        ])

        # ---------------------------------------------------------------------
        # Response
        # ---------------------------------------------------------------------

        return Response(
            {
                "success": True,

                "message": (
                    "Calculated field verification "
                    "completed successfully."
                ),

                "batch_id": str(
                    batch_id
                ),

                "professional_profile_id": (
                    professional.pk
                ),

                "submitted_count": len(
                    results
                ),

                "changed_count": len(
                    updated_results
                ),

                "skipped_count": len(
                    skipped_results
                ),

                "new_override_records": (
                    created_override_count
                ),

                "existing_override_records_updated": (
                    updated_override_count
                ),

                "new_history_records": len(
                    updated_results
                ),

                "updated_fields": (
                    updated_results
                ),

                "skipped_fields": (
                    skipped_results
                ),
            },
            status=status.HTTP_200_OK,
        )

@method_decorator(csrf_exempt, name="dispatch")
class OverrideCalculatedFieldAPIView(APIView):
    """
    POST : Create a CalculatedFieldOverride request. If the request body
    already carries a final decision of APPROVED (i.e. an admin acting
    directly, not a two-step recommend-then-approve flow), the override
    is applied immediately: the target field is updated and a
    CalculatedFieldValueHistory row is appended
    (change_source=OVERRIDE_APPROVED, linked back to the override).

    Body: all CalculatedFieldOverride fields (see CalculatedFieldOverrideSerializer).
    At minimum for immediate approval:
      {
        "tenant": <id>, "content_type": <id>, "object_id": <id>,
        "field_name": "current_qualion_level",
        "calculation_field_code": "QUALION_LEVEL",
        "professional": <id>,
        "request_type": "CORRECTION",
        "system_calculated_value": {"qualion_level": "L1"},
        "system_calculated_at": "...", "system_ruleset_version": "2026.1",
        "proposed_value": {"qualion_level": "L2"},
        "override_reason_code": "SOURCE_DATA_INCOMPLETE",
        "rationale": "...",
        "requested_by": <user_id>, "requested_at": "...",
        "decision": "APPROVED",
        "final_approved_value": {"qualion_level": "L2"},
        "approved_by": <user_id>, "approved_at": "...",
        "effective_from": "2026-08-12"
      }

    Omitting "decision"/"final_approved_value"/"approved_by" simply
    records the request as PENDING for later review via the existing
    CalculatedFieldOverrideRetrieveUpdateDeleteAPIView (PUT to approve).
    """

    permission_classes = [AllowAny]

    @extend_schema(request=CalculatedFieldOverrideSerializer)
    def post(self, request):
        serializer = CalculatedFieldOverrideSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        override = serializer.save()

        if override.decision != "APPROVED":
            return Response(
                {
                    "success": True,
                    "message": "Override request recorded; pending review.",
                    "data": CalculatedFieldOverrideSerializer(override).data,
                },
                status=status.HTTP_201_CREATED,
            )

        # Immediate approval path: apply to the target table and log history.
        target_model = override.content_type.model_class()
        try:
            target_instance = target_model.objects.get(pk=override.object_id)
        except target_model.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Override was recorded, but the target record no longer exists.",
                    "data": CalculatedFieldOverrideSerializer(override).data,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            field = target_model._meta.get_field(override.field_name)
        except Exception:
            return Response(
                {
                    "success": False,
                    "message": f"Field '{override.field_name}' does not exist on {target_model.__name__}.",
                    "data": CalculatedFieldOverrideSerializer(override).data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw_value = override.final_approved_value
        if field.is_relation:
            code = raw_value.get("code") if isinstance(raw_value, dict) else raw_value
            try:
                resolved_value = field.related_model.objects.get(code=code)
            except field.related_model.DoesNotExist:
                return Response(
                    {
                        "success": False,
                        "message": f"No {field.related_model.__name__} found with code={code!r}.",
                        "data": CalculatedFieldOverrideSerializer(override).data,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif isinstance(raw_value, dict) and "value" in raw_value:
            resolved_value = raw_value["value"]
        elif isinstance(raw_value, dict) and len(raw_value) == 1:
            resolved_value = next(iter(raw_value.values()))
        else:
            resolved_value = raw_value

        previous_raw, history = apply_calculated_value(
            tenant=override.tenant,
            professional=override.professional,
            target_instance=target_instance,
            field_name=override.field_name,
            calculation_field_code=override.calculation_field_code,
            resolved_value=resolved_value,
            new_value_raw=override.final_approved_value,
            ruleset_version=override.system_ruleset_version,
            change_source="OVERRIDE_APPROVED",
            override=override,
            changed_by=override.approved_by,
            effective_from=override.effective_from,
        )

        return Response(
            {
                "success": True,
                "message": "Override approved and applied successfully.",
                "data": {
                    "override": CalculatedFieldOverrideSerializer(override).data,
                    "previous_value": previous_raw,
                    "new_value": override.final_approved_value,
                    "history_id": history.pk,
                },
            },
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# 3. Recalculate all 11 fixed-formula fields for a professional in one
#    call. None of these read CalculationRuleSet/CalculationRule — see
#    FIXED_FIELD_CODES in governance_calculation_engine.py. The 3
#    genuinely rule-driven fields (QUALION_LEVEL, DEPLOYABILITY_FLAG,
#    CANDIDATE_MENTOR_CLASSIFICATION) are NOT touched here; keep using
#    CalculateSystemFieldAPIView for those.
# ============================================================


@method_decorator(csrf_exempt, name="dispatch")
class CalculateFixedSystemFieldsAPIView(APIView):
    """
    POST : Recalculate every fixed-formula system-calculated field for one
    professional and save each straight into its destination table,
    logging one CalculatedFieldValueHistory row per field
    (change_source=SYSTEM_RECALCULATION). Covers:

      Scoped (per Industry/Scope):
        Calendar Experience, Verified Field Days, Verified Project Count,
        Highest Authority Reached
      Profile-wide:
        Professional Headline, Professional Summary, Primary Role,
        Additional Roles, Industries Served, Total Career Experience
      Per-record:
        Credential Status (applied to every ACTIVE/EXPIRING_SOON/EXPIRED
        credential with an expiry_date), Project Responsibility Bullets
        (applied to every ProjectRecord whose responsibilities field is
        currently blank — never overwrites existing candidate text)

    Body:
      {
        "professional_id": <id>
      }

    Scoped fields run once per ScopeCatalog discovered from this
    professional's own project experience (distinct scopes behind their
    ProjectScope rows) — a ProfessionalScope row is created for any scope
    that doesn't already have one. There's no payload option to restrict
    or seed an arbitrary scope list; it's always everything their projects
    already touch.

    A failure on one field (e.g. no verified data yet for that scope)
    does not stop the rest — it comes back as one "ERROR" entry alongside
    the others' "SAVED" entries, so the response always reflects the full
    batch outcome, never just the first failure.
    """

    permission_classes = [AllowAny]

    @extend_schema(request=CalculateFixedSystemFieldsRequestSerializer)
    def post(self, request):
        professional_id = request.data.get("professional_id")

        if not professional_id:
            return Response(
                {"success": False, "message": "'professional_id' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            professional = ProfessionalProfile.objects.get(pk=professional_id)
        except ProfessionalProfile.DoesNotExist:
            return Response(
                {"success": False, "message": "Professional not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Scopes are always auto-discovered from this professional's own
        # project experience (see calculate_fixed_fields_for_professional) —
        # nothing in the payload can override that.
        results = calculate_fixed_fields_for_professional(professional, scopes=None)

        saved = sum(
            1
            for bucket in ("scopes", "profile", "credentials", "responsibilities")
            for r in results[bucket]
            if r["status"] == "SAVED"
        )
        errored = sum(
            1
            for bucket in ("scopes", "profile", "credentials", "responsibilities")
            for r in results[bucket]
            if r["status"] == "ERROR"
        )
        skipped = sum(
            1
            for bucket in ("scopes", "profile", "credentials", "responsibilities")
            for r in results[bucket]
            if r["status"] == "SKIPPED"
        )

        return Response(
            {
                "success": True,
                "message": f"Fixed-field recalculation complete: {saved} saved, "
                f"{errored} could not be calculated, {skipped} skipped.",
                "data": {
                    "professional": professional.pk,
                    "fields_covered": sorted(FIXED_FIELD_CODES),
                    **results,
                },
            },
            status=status.HTTP_200_OK,
        )
        

# ============================================================
# PROJECT VERIFICATION STATUSES REQUESTED BY YOU
# ============================================================

ALLOWED_PROJECT_VERIFICATION_STATUSES = [
    "SELF_DECLARED",
    "EVIDENCE_UPLOADED",
    "VERIFIED",
    "REJECTED",
]


# ============================================================
# AUTHORITY ORDER
# ============================================================
#
# Excel rule:
#
# "Highest verified authority level achieved on the standard
# ladder, from Observed through Technical Authority."
#
# IMPORTANT:
# These values should match catalog.ReferenceValue.code values
# stored for AUTHORITY_ACTION.
#
# Add/remove aliases below according to your actual master data.
# ============================================================

AUTHORITY_RANK = {
    "OBSERVED": 1,
    "OBSERVE": 1,

    "ASSISTED": 2,
    "ASSIST": 2,

    "PERFORMED": 3,
    "PERFORM": 3,
    "EXECUTED": 3,

    "REVIEWED": 4,
    "REVIEW": 4,

    "APPROVED": 5,
    "APPROVE": 5,

    "TECHNICAL_AUTHORITY": 6,
    "TECHNICAL AUTHORITY": 6,
    "TA": 6,
}


# ============================================================
# DATE HELPERS
# ============================================================

def months_between(start_date, end_date):
    """
    Calculate calendar month span.

    Example:
        2024-01-01 -> 2024-02-01 = 1
        2024-01-15 -> 2025-03-10 = 14

    Requirement says:
        first project start_date -> last project end_date
        and current date if end_date is NULL.

    We therefore calculate the difference between year/month
    components rather than summing individual project periods.
    """

    if not start_date or not end_date:
        return 0

    if end_date < start_date:
        return 0

    return (
        (end_date.year - start_date.year) * 12
        + (end_date.month - start_date.month)
    )


def project_duration_days(project, today):
    """
    Used to determine the longest project for primary_role.
    """

    if not project.start_date:
        return 0

    end_date = project.end_date or today

    if end_date < project.start_date:
        return 0

    return (end_date - project.start_date).days + 1


# ============================================================
# REFERENCE VALUE HELPERS
# ============================================================

def reference_value_code(reference):
    """
    Safely return ReferenceValue.code.

    Falls back to label/string only when required.
    """

    if not reference:
        return None

    code = getattr(reference, "code", None)

    if code:
        return str(code).strip().upper()

    label = getattr(reference, "label", None)

    if label:
        return str(label).strip().upper()

    return str(reference).strip().upper()


def reference_value_label(reference):
    """
    Human-readable ReferenceValue label.
    """

    if not reference:
        return ""

    label = getattr(reference, "label", None)

    if label:
        return str(label).strip()

    value = getattr(reference, "value", None)

    if value:
        return str(value).strip()

    code = getattr(reference, "code", None)

    if code:
        return str(code).replace("_", " ").title()

    return str(reference)


def reference_json_value(reference):
    """
    Value stored inside JSONField fields such as:
        additional_roles
        industries_served

    Prefer stable ReferenceValue code.

    Example:
        ["WELDING_INSPECTOR", "COATING_INSPECTOR"]
        ["OIL_GAS", "MARINE_OFFSHORE"]
    """

    if not reference:
        return None

    code = getattr(reference, "code", None)

    if code:
        return code

    return reference.pk


# ============================================================
# HIGHEST AUTHORITY
# ============================================================

def get_highest_authority(project_scope_rows):
    """
    Excel rule:

        Highest Authority Reached

        Based on:
            Authority level recorded per project,
            verification status.

        How it works:
            Highest VERIFIED authority achieved on the
            standard authority ladder.

    IMPORTANT:
        ProjectRecord may be SELF_DECLARED, etc.,
        but authority itself must be VERIFIED.

    Therefore only ProjectScope records with:
        verification_status == VERIFIED
    are considered here.
    """

    highest_authority = None
    highest_rank = 0

    for project_scope in project_scope_rows:

        # Sheet explicitly says VERIFIED authority.
        if project_scope.verification_status != "VERIFIED":
            continue

        authority = project_scope.authority_action

        if not authority:
            continue

        authority_code = reference_value_code(authority)

        if not authority_code:
            continue

        rank = AUTHORITY_RANK.get(authority_code, 0)

        if rank > highest_rank:
            highest_rank = rank
            highest_authority = authority

    return highest_authority


# ============================================================
# RESPONSIBILITY GENERATION
# ============================================================

def normalise_response_value(value):
    """
    Convert ScopeResponse JSONField value into readable text.
    """

    if value is None:
        return ""

    if isinstance(value, bool):
        return "Yes" if value else "No"

    if isinstance(value, list):
        return ", ".join(
            str(item)
            for item in value
            if item not in [None, ""]
        )

    if isinstance(value, dict):
        values = []

        for key, item in value.items():

            if item in [None, "", [], {}]:
                continue

            values.append(
                f"{str(key).replace('_', ' ').title()}: {item}"
            )

        return "; ".join(values)

    return str(value).strip()


def get_form_field_label(form_field):
    """
    Different versions of your model have used field_label / label.

    This supports either without breaking.
    """

    if not form_field:
        return ""

    label = getattr(form_field, "field_label", None)

    if label:
        return label

    label = getattr(form_field, "label", None)

    if label:
        return label

    field_code = getattr(form_field, "field_code", None)

    if field_code:
        return field_code.replace("_", " ").replace(".", " ").title()

    return str(form_field)


def generate_project_responsibilities(project):
    """
    Sheet rule:

        Project Responsibility Bullets

        Based on:
            Structured activity fields on each project.

        How it works:
            Draft automatically from structured data
            instead of unsupported free text.

    Sources used:
        ProjectScope.activity_summary
        ScopeResponse.form_field
        ScopeResponse.value

    No AI-generated/invented activities are added.
    """

    bullets = []
    seen = set()

    for project_scope in project.project_scopes.all():

        scope_name = getattr(
            project_scope.scope,
            "scope_name",
            str(project_scope.scope),
        )

        # ----------------------------------------------------
        # ProjectScope activity
        # ----------------------------------------------------

        activity_summary = (
            project_scope.activity_summary or ""
        ).strip()

        if activity_summary:

            bullet = (
                f"{scope_name}: {activity_summary}"
            )

            if bullet not in seen:
                bullets.append(bullet)
                seen.add(bullet)

        # ----------------------------------------------------
        # ScopeResponse structured values
        # ----------------------------------------------------

        for response in project_scope.scope_responses.all():

            value = normalise_response_value(response.value)

            if not value:
                continue

            field_label = get_form_field_label(
                response.form_field
            )

            bullet = (
                f"{scope_name} - "
                f"{field_label}: {value}"
            )

            if bullet not in seen:
                bullets.append(bullet)
                seen.add(bullet)

    if not bullets:
        return ""

    return "\n".join(
        f"• {bullet}"
        for bullet in bullets
    )


# ============================================================
# PROFILE HEADLINE
# ============================================================

def generate_headline(
    professional_scope_records,
    primary_role,
):
    """
    Excel:

        Headline is based on:
            Verified level + industry + scope.

    We choose the strongest available ProfessionalScope record.

    Priority:
        current_qualion_level
        authority
        calendar experience

    If current_qualion_level has not yet been calculated,
    headline falls back to:
        Primary Role | Scope | Industry

    This avoids inventing a Qualion level.
    """

    if not professional_scope_records:
        if primary_role:
            return reference_value_label(primary_role)[:140]

        return ""

    def scope_sort_key(record):

        level = getattr(
            record,
            "current_qualion_level",
            None,
        )

        level_code = reference_value_code(level) or ""

        level_number = 0

        if level_code.startswith("L"):
            try:
                level_number = int(
                    level_code.replace("L", "")
                )
            except ValueError:
                level_number = 0

        authority = getattr(
            record,
            "highest_authority_reached",
            None,
        )

        authority_rank = AUTHORITY_RANK.get(
            reference_value_code(authority),
            0,
        )

        experience = (
            record.calendar_experience_months or 0
        )

        return (
            level_number,
            authority_rank,
            experience,
        )

    best_scope = max(
        professional_scope_records,
        key=scope_sort_key,
    )

    level = getattr(
        best_scope,
        "current_qualion_level",
        None,
    )

    scope = getattr(
        best_scope,
        "scope",
        None,
    )

    industry = (
        scope.industry
        if scope and scope.industry_id
        else None
    )

    parts = []

    if level:
        parts.append(reference_value_label(level))

    if primary_role:
        parts.append(reference_value_label(primary_role))

    if scope:
        scope_name = getattr(
            scope,
            "scope_name",
            str(scope),
        )

        parts.append(scope_name)

    if industry:
        parts.append(
            reference_value_label(industry)
        )

    # Remove duplicates while retaining order
    unique_parts = []

    for part in parts:

        if (
            part
            and part.lower()
            not in [
                x.lower()
                for x in unique_parts
            ]
        ):
            unique_parts.append(part)

    headline = " | ".join(unique_parts)

    return headline[:140]


# ============================================================
# PROFILE SUMMARY
# ============================================================

def generate_summary(
    profile,
    professional_scope_records,
    primary_role,
    additional_roles,
    industries,
    career_months,
):
    """
    Excel:

        Professional Summary

        Based on:
            Full structured profile.

        How it works:
            System drafts summary from facts on file.
            It must not invent unsupported claims.

    Therefore this only uses stored/calculated values.
    """

    parts = []

    name = (
        profile.display_name
        or profile.legal_full_name
        or ""
    )

    primary_role_name = (
        reference_value_label(primary_role)
        if primary_role
        else ""
    )

    # --------------------------------------------------------
    # Opening
    # --------------------------------------------------------

    if name and primary_role_name:
        parts.append(
            f"{name} is a {primary_role_name} "
            f"with {career_months} months of recorded "
            f"project experience."
        )

    elif primary_role_name:
        parts.append(
            f"Professional with primary experience as "
            f"{primary_role_name} and {career_months} months "
            f"of recorded project experience."
        )

    elif career_months:
        parts.append(
            f"Professional with {career_months} months "
            f"of recorded project experience."
        )

    # --------------------------------------------------------
    # Industries
    # --------------------------------------------------------

    industry_names = [
        reference_value_label(industry)
        for industry in industries
        if industry
    ]

    if industry_names:
        parts.append(
            "Industry experience includes "
            + ", ".join(industry_names)
            + "."
        )

    # --------------------------------------------------------
    # Scopes
    # --------------------------------------------------------

    scope_names = []

    for professional_scope in professional_scope_records:

        scope = getattr(
            professional_scope,
            "scope",
            None,
        )

        if not scope:
            continue

        scope_name = getattr(
            scope,
            "scope_name",
            str(scope),
        )

        if scope_name not in scope_names:
            scope_names.append(scope_name)

    if scope_names:
        parts.append(
            "Recorded scope experience includes "
            + ", ".join(scope_names)
            + "."
        )

    # --------------------------------------------------------
    # Highest authority
    # --------------------------------------------------------

    authorities = []

    for professional_scope in professional_scope_records:

        authority = getattr(
            professional_scope,
            "highest_authority_reached",
            None,
        )

        if authority:
            authorities.append(authority)

    if authorities:

        highest = max(
            authorities,
            key=lambda authority: AUTHORITY_RANK.get(
                reference_value_code(authority),
                0,
            ),
        )

        authority_name = reference_value_label(
            highest
        )

        if authority_name:
            parts.append(
                f"Highest verified authority recorded is "
                f"{authority_name}."
            )

    # --------------------------------------------------------
    # Additional roles
    # --------------------------------------------------------

    additional_role_names = [
        reference_value_label(role)
        for role in additional_roles
        if role
    ]

    if additional_role_names:
        parts.append(
            "Additional recorded roles include "
            + ", ".join(additional_role_names)
            + "."
        )

    return " ".join(parts)[:2000]


# ============================================================
# CREDENTIAL STATUS
# ============================================================

def calculate_credential_status(
    credential,
    today,
):
    """
    Current model supports:

        DRAFT
        ACTIVE
        EXPIRED
        REVOKED
        ARCHIVED

    Rules:

    1. REVOKED stays REVOKED.
    2. ARCHIVED stays ARCHIVED.
    3. expiry_date before today -> EXPIRED.
    4. end_date before today -> EXPIRED.
    5. start_date in future -> DRAFT.
    6. issue_date in future -> DRAFT.
    7. Otherwise -> ACTIVE.

    We DO NOT automatically overwrite REVOKED/ARCHIVED.
    """

    if credential.status in [
        "REVOKED",
        "ARCHIVED",
    ]:
        return credential.status

    if (
        credential.expiry_date
        and credential.expiry_date < today
    ):
        return "EXPIRED"

    if (
        credential.end_date
        and credential.end_date < today
    ):
        return "EXPIRED"

    if (
        credential.start_date
        and credential.start_date > today
    ):
        return "DRAFT"

    if (
        credential.issue_date
        and credential.issue_date > today
    ):
        return "DRAFT"

    return "ACTIVE"


# ============================================================
# MAIN API
# ============================================================


@method_decorator(csrf_exempt, name="dispatch")
class ProfessionalCalculatedFieldsAPIView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "professional_profile_id": {
                        "type": "string",
                        "format": "uuid",
                    },
                },
                "required": [
                    "professional_profile_id"
                ],
            }
        },
        description=(
            "Recalculate ProfessionalScope, ProfessionalProfile, "
            "ProjectRecord responsibilities and CredentialRecord "
            "status from structured professional experience data."
        ),
    )
    @transaction.atomic
    def post(self, request):

        # ====================================================
        # 1. PROFESSIONAL PROFILE ID
        # ====================================================

        professional_profile_id = request.data.get(
            "professional_profile_id"
        )

        if not professional_profile_id:
            return Response(
                {
                    "success": False,
                    "message": (
                        "professional_profile_id is required."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            profile = (
                ProfessionalProfile.objects
                .select_for_update()
                .get(
                    pk=professional_profile_id
                )
            )

        except ProfessionalProfile.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": (
                        "ProfessionalProfile not found."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        today = timezone.localdate()

        # ====================================================
        # 2. FETCH PROJECTS
        # ====================================================
        #
        # ProjectRecord
        #     -> ProjectScope
        #         -> ScopeResponse
        #
        # Everything fetched upfront to avoid N+1 queries.
        # ====================================================

        scope_response_queryset = (
            ScopeResponse.objects
            .select_related(
                "form_field"
            )
            .order_by(
                "repeat_index"
            )
        )

        project_scope_queryset = (
            ProjectScope.objects
            .select_related(
                "scope",
                "scope__industry",
                "authority_action",
            )
            .prefetch_related(
                Prefetch(
                    "scope_responses",
                    queryset=scope_response_queryset,
                )
            )
        )

        projects = list(
            ProjectRecord.objects
            .filter(
                professional=profile,
                verification_status__in=(
                    ALLOWED_PROJECT_VERIFICATION_STATUSES
                ),
            )
            .select_related(
                "role_title",
                "industry_classification",
            )
            .prefetch_related(
                Prefetch(
                    "project_scopes",
                    queryset=project_scope_queryset,
                )
            )
            .order_by(
                "start_date"
            )
        )

        # No project experience
        if not projects:

            return Response(
                {
                    "success": False,
                    "message": (
                        "No eligible ProjectRecord records "
                        "found for this professional."
                    ),
                    "professional_profile_id": str(
                        profile.pk
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ====================================================
        # 3. GROUP PROJECTS BY SCOPE
        # ====================================================

        scope_groups = defaultdict(list)

        for project in projects:

            for project_scope in (
                project.project_scopes.all()
            ):

                scope_groups[
                    project_scope.scope_id
                ].append(
                    {
                        "project": project,
                        "project_scope": project_scope,
                    }
                )

        # ====================================================
        # 4. CREATE / UPDATE PROFESSIONAL SCOPE
        # ====================================================

        calculated_professional_scopes = []

        professional_scope_response = []

        for scope_id, rows in scope_groups.items():

            first_project_scope = rows[0][
                "project_scope"
            ]

            scope = first_project_scope.scope

            # ScopeCatalog already carries industry
            industry = scope.industry

            # -----------------------------------------------
            # Get unique project records
            # -----------------------------------------------

            unique_projects = {}

            for row in rows:

                project = row["project"]

                unique_projects[
                    str(project.pk)
                ] = project

            grouped_projects = list(
                unique_projects.values()
            )

            # -----------------------------------------------
            # A. calendar_experience_months
            # -----------------------------------------------

            grouped_projects.sort(
                key=lambda project: project.start_date
            )

            first_start_date = min(
                project.start_date
                for project in grouped_projects
                if project.start_date
            )

            last_end_date = max(
                (
                    project.end_date
                    or today
                )
                for project in grouped_projects
            )

            calendar_experience_months = (
                months_between(
                    first_start_date,
                    last_end_date,
                )
            )

            # -----------------------------------------------
            # B. verified_field_days
            # -----------------------------------------------

            verified_field_days = sum(
                (
                    project.verified_field_days
                    or Decimal("0")
                )
                for project in grouped_projects
            )

            # -----------------------------------------------
            # C. verified_project_count
            # -----------------------------------------------

            verified_project_count = len(
                grouped_projects
            )

            # -----------------------------------------------
            # D. highest_authority_reached
            # -----------------------------------------------
            #
            # IMPORTANT:
            # Only VERIFIED ProjectScope authority values
            # participate because this is the Excel rule.
            # -----------------------------------------------

            grouped_project_scopes = [
                row["project_scope"]
                for row in rows
            ]

            highest_authority = (
                get_highest_authority(
                    grouped_project_scopes
                )
            )

            # -----------------------------------------------
            # CREATE / UPDATE
            # -----------------------------------------------
            #
            # Assumes your ProfessionalScope has:
            #
            # professional
            # tenant
            # industry
            # scope
            #
            # and calculated fields named exactly as supplied.
            # -----------------------------------------------

            professional_scope, created = (
                ProfessionalScope.objects
                .update_or_create(
                    professional=profile,
                    scope=scope,
                    defaults={
                        "tenant": profile.tenant,
                        "calendar_experience_months":
                            calendar_experience_months,
                        "verified_field_days":
                            verified_field_days,
                        "verified_project_count":
                            verified_project_count,
                        "highest_authority_reached":
                            highest_authority,
                        "last_recalculated_at":
                            timezone.now(),
                    },
                )
            )

            calculated_professional_scopes.append(
                professional_scope
            )

            professional_scope_response.append(
                {
                    "id": str(professional_scope.pk),
                    "created": created,

                    # ProfessionalScope does not contain industry directly.
                    # Industry comes from ScopeCatalog.
                    "industry_id": (
                        scope.industry_id
                        if scope.industry_id
                        else None
                    ),
                    "industry": (
                        reference_value_label(scope.industry)
                        if scope.industry_id
                        else None
                    ),

                    "scope_id": scope.pk,
                    "scope": getattr(
                        scope,
                        "scope_name",
                        str(scope),
                    ),

                    "calendar_experience_months":
                        calendar_experience_months,

                    "verified_field_days":
                        float(verified_field_days),

                    "verified_project_count":
                        verified_project_count,

                    "highest_authority_reached": (
                        reference_value_label(
                            highest_authority
                        )
                        if highest_authority
                        else None
                    ),
                }
            )

        # ====================================================
        # 5. CALCULATE TOTAL CAREER EXPERIENCE
        # ====================================================
        #
        # Your latest requirement:
        #
        # first project start_date
        #        ->
        # last project end_date/current date
        #
        # across ALL scopes.
        # ====================================================

        all_start_dates = [
            project.start_date
            for project in projects
            if project.start_date
        ]

        all_end_dates = [
            project.end_date or today
            for project in projects
        ]

        career_experience_months = 0

        if all_start_dates and all_end_dates:

            career_experience_months = (
                months_between(
                    min(all_start_dates),
                    max(all_end_dates),
                )
            )

        # ====================================================
        # 6. PRIMARY ROLE
        # ====================================================
        #
        # Your rule:
        #
        # role_title belonging to project record having
        # maximum experience duration.
        # ====================================================

        projects_with_role = [
            project
            for project in projects
            if project.role_title_id
        ]

        primary_role = None

        if projects_with_role:

            longest_project = max(
                projects_with_role,
                key=lambda project:
                    project_duration_days(
                        project,
                        today,
                    ),
            )

            primary_role = (
                longest_project.role_title
            )

        # ====================================================
        # 7. ADDITIONAL ROLES
        # ====================================================

        additional_role_objects = []

        seen_role_ids = set()

        for project in projects:

            role = project.role_title

            if not role:
                continue

            if (
                primary_role
                and role.pk == primary_role.pk
            ):
                continue

            if role.pk in seen_role_ids:
                continue

            seen_role_ids.add(role.pk)

            additional_role_objects.append(
                role
            )

        additional_roles_json = [
            reference_json_value(role)
            for role in additional_role_objects
        ]

        # ====================================================
        # 8. INDUSTRIES SERVED
        # ====================================================

        industry_objects = []

        seen_industry_ids = set()

        for project in projects:

            industry = (
                project.industry_classification
            )

            if not industry:
                continue

            if industry.pk in seen_industry_ids:
                continue

            seen_industry_ids.add(
                industry.pk
            )

            industry_objects.append(
                industry
            )

        industries_served_json = [
            reference_json_value(industry)
            for industry in industry_objects
        ]

        # ====================================================
        # 9. HEADLINE
        # ====================================================

        headline = generate_headline(
            calculated_professional_scopes,
            primary_role,
        )

        # ====================================================
        # 10. SUMMARY
        # ====================================================

        summary = generate_summary(
            profile=profile,
            professional_scope_records=(
                calculated_professional_scopes
            ),
            primary_role=primary_role,
            additional_roles=(
                additional_role_objects
            ),
            industries=industry_objects,
            career_months=(
                career_experience_months
            ),
        )

        # ====================================================
        # 11. UPDATE PROFESSIONAL PROFILE
        # ====================================================

        profile.headline = headline
        profile.summary = summary

        profile.summary_source = (
            ProfessionalProfile
            .SummarySource
            .SYSTEM_GENERATED
        )

        profile.primary_role = primary_role

        profile.additional_roles = (
            additional_roles_json
        )

        profile.industries_served = (
            industries_served_json
        )

        # Your actual model field from previous implementation
        # is total_career_experience_months.
        profile.total_career_experience_months = (
            career_experience_months
        )

        profile.save(
            update_fields=[
                "headline",
                "summary",
                "summary_source",
                "primary_role",
                "additional_roles",
                "industries_served",
                "total_career_experience_months",
                "updated_at",
            ]
        )

        # ====================================================
        # 12. UPDATE PROJECT RESPONSIBILITIES
        # ====================================================

        updated_projects = []

        for project in projects:

            generated_responsibilities = (
                generate_project_responsibilities(
                    project
                )
            )

            # Do not destroy existing content when
            # structured data contains nothing.
            if generated_responsibilities:

                project.responsibilities = (
                    generated_responsibilities
                )

                project.save(
                    update_fields=[
                        "responsibilities",
                        "updated_at",
                    ]
                )

                updated_projects.append(
                    {
                        "project_id": str(
                            project.pk
                        ),
                        "project_name":
                            project.project_name,
                        "responsibilities":
                            generated_responsibilities,
                    }
                )

        # ====================================================
        # 13. UPDATE CREDENTIAL STATUS
        # ====================================================

        credentials = (
            CredentialRecord.objects
            .select_for_update()
            .filter(
                professional=profile
            )
        )

        updated_credentials = []

        for credential in credentials:

            old_status = credential.status

            new_status = (
                calculate_credential_status(
                    credential,
                    today,
                )
            )

            if old_status != new_status:

                credential.status = new_status

                credential.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

            updated_credentials.append(
                {
                    "credential_id": str(
                        credential.pk
                    ),
                    "title": credential.title,
                    "old_status": old_status,
                    "new_status": new_status,
                    "issue_date": (
                        credential.issue_date
                        if credential.issue_date
                        else None
                    ),
                    "start_date": (
                        credential.start_date
                        if credential.start_date
                        else None
                    ),
                    "end_date": (
                        credential.end_date
                        if credential.end_date
                        else None
                    ),
                    "expiry_date": (
                        credential.expiry_date
                        if credential.expiry_date
                        else None
                    ),
                }
            )

        # ====================================================
        # 14. SUCCESS RESPONSE
        # ====================================================

        return Response(
            {
                "success": True,
                "message": (
                    "Professional calculated fields "
                    "updated successfully."
                ),
                "data": {
                    "professional_profile": {
                        "id": str(profile.pk),
                        "headline":
                            profile.headline,
                        "summary":
                            profile.summary,
                        "summary_source":
                            profile.summary_source,
                        "primary_role": (
                            reference_value_label(
                                primary_role
                            )
                            if primary_role
                            else None
                        ),
                        "additional_roles":
                            additional_roles_json,
                        "industries_served":
                            industries_served_json,
                        "total_career_experience_months":
                            career_experience_months,
                    },

                    "professional_scopes":
                        professional_scope_response,

                    "updated_projects":
                        updated_projects,

                    "credentials":
                        updated_credentials,
                },
            },
            status=status.HTTP_200_OK,
        )
                
        
      
      
      
# ============================================================
# BASIC HELPERS
# ============================================================

def get_reference_rank(reference_value):
    """
    Returns ReferenceValue.sort_order.

    Used for:
        QUALION_LEVEL
        AUTHORITY_STATUS
        COMPLEXITY
    """
    if not reference_value:
        return None

    return getattr(reference_value, "sort_order", None)


def numeric_range_satisfied(actual_value, minimum_value=None, maximum_value=None):
    """
    Checks numeric value against optional minimum and maximum.

    Examples:
        min=12, max=24, actual=18 -> True
        min=12, max=24, actual=30 -> False
        min=12, max=None, actual=18 -> True
        min=None, max=24, actual=18 -> True

    If both minimum and maximum are empty, condition is ignored.
    """
    if minimum_value is None and maximum_value is None:
        return True

    if actual_value is None:
        return False

    if minimum_value is not None and actual_value < minimum_value:
        return False

    if maximum_value is not None and actual_value > maximum_value:
        return False

    return True


def reference_range_satisfied(actual_value, minimum_value=None, maximum_value=None):
    """
    Checks ReferenceValue using sort_order.

    Example:
        minimum = L2
        maximum = L4
        actual = L3

        L2.sort_order <= L3.sort_order <= L4.sort_order
    """
    if minimum_value is None and maximum_value is None:
        return True

    if actual_value is None:
        return False

    actual_rank = get_reference_rank(actual_value)

    if actual_rank is None:
        return False

    if minimum_value is not None:
        minimum_rank = get_reference_rank(minimum_value)

        if minimum_rank is None or actual_rank < minimum_rank:
            return False

    if maximum_value is not None:
        maximum_rank = get_reference_rank(maximum_value)

        if maximum_rank is None or actual_rank > maximum_rank:
            return False

    return True


def minimum_reference_satisfied(actual_value, minimum_value):
    """
    Minimum-only ReferenceValue comparison.
    """
    return reference_range_satisfied(actual_value, minimum_value=minimum_value)


# ============================================================
# CALCULATION RULE SCOPE HELPERS
# ============================================================

def get_rule_scope_ids(rule):
    """
    CalculationRule.scope is now ManyToManyField.

    Empty scope list means tenant-wide.
    """
    return {scope.pk for scope in rule.scope.all()}


def is_tenant_wide_rule(rule):
    """
    Empty CalculationRule.scope = tenant-wide rule.
    """
    return len(get_rule_scope_ids(rule)) == 0


def rule_applies_to_professional_scope(rule, professional_scope):
    """
    Returns True when the ProfessionalScope's ScopeCatalog is one of
    the scopes selected in CalculationRule.scope.
    """
    return professional_scope.scope_id in get_rule_scope_ids(rule)


# ============================================================
# PROFESSIONAL SCOPE HELPERS
# ============================================================

def get_scope_authority(professional_scope):
    """
    Prefer current_authority_status if available.

    Your existing 12-field calculation stores
    highest_authority_reached, so this is used as fallback.
    """
    current_authority = getattr(professional_scope, "current_authority_status", None)

    if current_authority:
        return current_authority

    return getattr(professional_scope, "highest_authority_reached", None)


def get_scope_complexity(professional_scope):
    """
    Complexity parameter used by QUALION_LEVEL rules.
    """
    return getattr(professional_scope, "complexity_rating", None)


# ============================================================
# CREDENTIAL HELPERS
# ============================================================

def get_reference_identifier(reference_value):
    """
    Returns multiple possible identifiers from a ReferenceValue.
    This helps when CredentialRecord.record_type is stored as a string
    while CalculationRule.required_credential_types stores ReferenceValue.
    """
    if reference_value is None:
        return set()

    values = {str(reference_value.pk)}

    for field_name in ["code", "value", "name"]:
        field_value = getattr(reference_value, field_name, None)

        if field_value:
            values.add(str(field_value).strip().upper())

    return values


def credential_type_matches(credential, required_type):
    """
    Supports either:
        CredentialRecord.credential_type -> ReferenceValue
    or:
        CredentialRecord.record_type -> string/ReferenceValue
    """
    credential_type = getattr(credential, "credential_type", None)

    if credential_type is not None:
        if hasattr(credential_type, "pk"):
            return credential_type.pk == required_type.pk

        return str(credential_type).strip().upper() in get_reference_identifier(required_type)

    record_type = getattr(credential, "record_type", None)

    if record_type is None:
        return False

    if hasattr(record_type, "pk"):
        return record_type.pk == required_type.pk

    return str(record_type).strip().upper() in get_reference_identifier(required_type)


def credential_matches_scope(credential, professional_scope):
    """
    If CredentialRecord contains a scope relation, require same scope.

    If CredentialRecord has no scope field or scope is empty,
    treat the credential as professional-wide.
    """
    credential_scope = getattr(credential, "scope", None)

    if credential_scope is None:
        return True

    if hasattr(credential_scope, "all"):
        credential_scope_ids = {scope.pk for scope in credential_scope.all()}
        return not credential_scope_ids or professional_scope.scope_id in credential_scope_ids

    if hasattr(credential_scope, "pk"):
        return credential_scope.pk == professional_scope.scope_id

    return True


def get_matching_credentials(rule, professional_scope, credentials):
    """
    Returns credentials satisfying the CalculationRule conditions:

        required_credential_types
        require_active_credential
        max_days_to_credential_expiry
        scope
    """
    required_types = list(rule.required_credential_types.all())

    if not required_types:
        return []

    today = timezone.localdate()
    matches = []

    for credential in credentials:
        if not credential_matches_scope(credential, professional_scope):
            continue

        if not any(credential_type_matches(credential, required_type) for required_type in required_types):
            continue

        if rule.require_active_credential:
            credential_status = getattr(credential, "status", None)

            if credential_status != "ACTIVE":
                continue

        if rule.max_days_to_credential_expiry is not None:
            expiry_date = getattr(credential, "expiry_date", None)

            if expiry_date is None:
                continue

            days_remaining = (expiry_date - today).days

            if days_remaining < 0:
                continue

            if days_remaining > rule.max_days_to_credential_expiry:
                continue

        matches.append(credential)

    return matches


def credential_condition_satisfied(rule, professional_scope, credentials):
    """
    At least one credential must match when required_credential_types
    contains values.

    If no credential types are configured, the condition is ignored.
    """
    required_types = list(rule.required_credential_types.all())

    if not required_types:
        return True

    return bool(get_matching_credentials(rule, professional_scope, credentials))


# ============================================================
# ASSESSMENT HELPERS
# ============================================================

def get_latest_assessment(professional_scope):
    """
    Gets latest CompetencyAssessment for this ProfessionalScope.
    """
    return CompetencyAssessment.objects.filter(professional_scope=professional_scope).order_by("-created_at").first()


def has_unresolved_reclassification_rejection(profile):
    """
    Checks whether professional has unresolved REJECTED
    ProfessionalReview of type RECLASSIFICATION.
    """
    model_fields = {field.name for field in ProfessionalReview._meta.get_fields()}
    filters = {"professional": profile}

    if "review_type" in model_fields:
        filters["review_type"] = "RECLASSIFICATION"

    if "decision" in model_fields:
        filters["decision"] = "REJECTED"
    elif "status" in model_fields:
        filters["status"] = "REJECTED"
    else:
        return False

    queryset = ProfessionalReview.objects.filter(**filters)

    if "resolved_at" in model_fields:
        queryset = queryset.filter(resolved_at__isnull=True)

    return queryset.exists()


# ============================================================
# RULE EVALUATION
# ============================================================

# def evaluate_rule(rule, professional_scope, profile, credentials):
#     """
#     Evaluates one CalculationRule against one ProfessionalScope.

#     ALL_CONDITIONS:
#         Every populated logical condition must match.

#     ANY_CONDITION:
#         At least one populated logical condition must match.

#     Important:
#         min/max belong to ONE logical range condition.

#     Example:
#         min_calendar_experience_months = 12
#         max_calendar_experience_months = 24

#     Becomes:
#         12 <= actual <= 24
#     """
#     checks = []
#     field_code = rule.calculation_field_code
#     authority = get_scope_authority(professional_scope)

#     # ========================================================
#     # 1. QUALION LEVEL
#     # ========================================================

#     if field_code == CalculatedFieldCode.QUALION_LEVEL:

#         # Calendar experience range
#         if rule.min_calendar_experience_months is not None or rule.max_calendar_experience_months is not None:
#             actual_value = professional_scope.calendar_experience_months or 0
#             checks.append(numeric_range_satisfied(actual_value, rule.min_calendar_experience_months, rule.max_calendar_experience_months))

#         # Verified field days range
#         if rule.min_verified_field_days is not None or rule.max_verified_field_days is not None:
#             actual_value = professional_scope.verified_field_days or Decimal("0")
#             checks.append(numeric_range_satisfied(actual_value, rule.min_verified_field_days, rule.max_verified_field_days))

#         # Verified project count range
#         if rule.min_verified_project_count is not None or rule.max_verified_project_count is not None:
#             actual_value = professional_scope.verified_project_count or 0
#             checks.append(numeric_range_satisfied(actual_value, rule.min_verified_project_count, rule.max_verified_project_count))

#         # Minimum authority
#         if rule.min_authority_status_id:
#             checks.append(minimum_reference_satisfied(authority, rule.min_authority_status))

#         # Minimum complexity
#         if rule.min_complexity_rating_id:
#             actual_complexity = get_scope_complexity(professional_scope)
#             checks.append(minimum_reference_satisfied(actual_complexity, rule.min_complexity_rating))

#         # Required credentials
#         if rule.required_credential_types.all():
#             checks.append(credential_condition_satisfied(rule, professional_scope, credentials))

#     # ========================================================
#     # 2. DEPLOYABILITY FLAG
#     # ========================================================

#     elif field_code == CalculatedFieldCode.DEPLOYABILITY_FLAG:

#         # Qualion level range
#         if rule.min_qualion_level_id or rule.max_qualion_level_id:
#             checks.append(reference_range_satisfied(professional_scope.current_qualion_level, rule.min_qualion_level, rule.max_qualion_level))

#         # Minimum authority
#         if rule.min_authority_status_id:
#             checks.append(minimum_reference_satisfied(authority, rule.min_authority_status))

#         # Credentials, active status and expiry
#         if rule.required_credential_types.all():
#             checks.append(credential_condition_satisfied(rule, professional_scope, credentials))

#     # ========================================================
#     # 3. CANDIDATE / MENTOR CLASSIFICATION
#     # ========================================================

#     elif field_code == CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION:

#         # Qualion level range
#         if rule.min_qualion_level_id or rule.max_qualion_level_id:
#             checks.append(reference_range_satisfied(professional_scope.current_qualion_level, rule.min_qualion_level, rule.max_qualion_level))

#         # Minimum authority
#         if rule.min_authority_status_id:
#             checks.append(minimum_reference_satisfied(authority, rule.min_authority_status))

#         latest_assessment = None

#         if rule.min_ethics_independence_score is not None or rule.require_latest_assessment_decision:
#             latest_assessment = get_latest_assessment(professional_scope)

#         # Minimum ethics score
#         if rule.min_ethics_independence_score is not None:
#             actual_score = getattr(latest_assessment, "ethics_independence_score", None) if latest_assessment else None
#             checks.append(actual_score is not None and actual_score >= rule.min_ethics_independence_score)

#         # Required latest assessment decision
#         if rule.require_latest_assessment_decision:
#             actual_decision = getattr(latest_assessment, "decision", None) if latest_assessment else None
#             checks.append(actual_decision == rule.require_latest_assessment_decision)

#         # Pending rejection block
#         if rule.block_if_pending_rejection:
#             checks.append(not has_unresolved_reclassification_rejection(profile))

#     # ========================================================
#     # MATCH RESULT
#     # ========================================================

#     # Empty rule can act as final/default fallback rule
#     if not checks:
#         return True

#     if rule.match_type == CalculationRule.MatchType.ANY_CONDITION:
#         return any(checks)

#     return all(checks)

def debug_reference_value(reference_value):
    if reference_value is None:
        return None

    return {
        "id": reference_value.pk,
        "code": getattr(reference_value, "code", None),
        "name": getattr(reference_value, "name", None),
        "value": getattr(reference_value, "value", None),
        "sort_order": getattr(reference_value, "sort_order", None),
        "display": str(reference_value),
    }


def print_condition_debug(field_name, actual_value, expected_value, result):
    print("")
    print(f"        FIELD CHECK : {field_name}")
    print(f"        USER VALUE  : {actual_value}")
    print(f"        RULE VALUE  : {expected_value}")
    print(f"        RESULT      : {'PASSED' if result else 'FAILED'}")


def evaluate_rule(rule, professional_scope, profile, credentials):
    checks = []
    field_code = rule.calculation_field_code
    authority = get_scope_authority(professional_scope)

    print("")
    print("=" * 100)
    print("CHECKING CALCULATION RULE")
    print("=" * 100)
    print(f"Rule ID            : {rule.pk}")
    print(f"Rule Label         : {rule.label}")
    print(f"Calculation Field  : {field_code}")
    print(f"Sequence           : {rule.sequence}")
    print(f"Match Type         : {rule.match_type}")
    print(f"Professional ID    : {profile.pk}")
    print(f"Professional Scope : {professional_scope.pk}")
    print(f"Scope ID           : {professional_scope.scope_id}")
    print(f"Scope              : {professional_scope.scope}")
    print("-" * 100)

    # ========================================================
    # 1. QUALION LEVEL
    # ========================================================

    if field_code == CalculatedFieldCode.QUALION_LEVEL:

        print("CALCULATING: QUALION_LEVEL")

        # Calendar experience
        if rule.min_calendar_experience_months is not None or rule.max_calendar_experience_months is not None:
            actual_value = professional_scope.calendar_experience_months or 0
            result = numeric_range_satisfied(actual_value, rule.min_calendar_experience_months, rule.max_calendar_experience_months)

            print_condition_debug(
                "calendar_experience_months",
                actual_value,
                {
                    "min": rule.min_calendar_experience_months,
                    "max": rule.max_calendar_experience_months,
                },
                result,
            )

            checks.append(result)

        # Verified field days
        if rule.min_verified_field_days is not None or rule.max_verified_field_days is not None:
            actual_value = professional_scope.verified_field_days or Decimal("0")
            result = numeric_range_satisfied(actual_value, rule.min_verified_field_days, rule.max_verified_field_days)

            print_condition_debug(
                "verified_field_days",
                actual_value,
                {
                    "min": rule.min_verified_field_days,
                    "max": rule.max_verified_field_days,
                },
                result,
            )

            checks.append(result)

        # Verified project count
        if rule.min_verified_project_count is not None or rule.max_verified_project_count is not None:
            actual_value = professional_scope.verified_project_count or 0
            result = numeric_range_satisfied(actual_value, rule.min_verified_project_count, rule.max_verified_project_count)

            print_condition_debug(
                "verified_project_count",
                actual_value,
                {
                    "min": rule.min_verified_project_count,
                    "max": rule.max_verified_project_count,
                },
                result,
            )

            checks.append(result)

        # Minimum authority
        if rule.min_authority_status_id:
            result = minimum_reference_satisfied(authority, rule.min_authority_status)

            print_condition_debug(
                "authority_status",
                debug_reference_value(authority),
                {
                    "minimum": debug_reference_value(rule.min_authority_status),
                },
                result,
            )

            checks.append(result)

        # Minimum complexity
        if rule.min_complexity_rating_id:
            actual_complexity = get_scope_complexity(professional_scope)
            result = minimum_reference_satisfied(actual_complexity, rule.min_complexity_rating)

            print_condition_debug(
                "complexity_rating",
                debug_reference_value(actual_complexity),
                {
                    "minimum": debug_reference_value(rule.min_complexity_rating),
                },
                result,
            )

            checks.append(result)

        # Credentials
        required_types = list(rule.required_credential_types.all())

        if required_types:
            matching_credentials = get_matching_credentials(rule, professional_scope, credentials)
            result = bool(matching_credentials)

            print_condition_debug(
                "required_credentials",
                {
                    "professional_credentials": [
                        {
                            "id": credential.pk,
                            "record_type": getattr(credential, "record_type", None),
                            "status": getattr(credential, "status", None),
                            "expiry_date": getattr(credential, "expiry_date", None),
                        }
                        for credential in credentials
                    ],
                    "matching_credentials": [
                        credential.pk for credential in matching_credentials
                    ],
                },
                {
                    "required_types": [
                        debug_reference_value(required_type)
                        for required_type in required_types
                    ],
                    "require_active_credential": rule.require_active_credential,
                    "max_days_to_credential_expiry": rule.max_days_to_credential_expiry,
                },
                result,
            )

            checks.append(result)

    # ========================================================
    # 2. DEPLOYABILITY FLAG
    # ========================================================

    elif field_code == CalculatedFieldCode.DEPLOYABILITY_FLAG:

        print("CALCULATING: DEPLOYABILITY_FLAG")

        # Qualion range
        if rule.min_qualion_level_id or rule.max_qualion_level_id:
            actual_value = professional_scope.current_qualion_level

            result = reference_range_satisfied(
                actual_value,
                rule.min_qualion_level,
                rule.max_qualion_level,
            )

            print_condition_debug(
                "current_qualion_level",
                debug_reference_value(actual_value),
                {
                    "min": debug_reference_value(rule.min_qualion_level),
                    "max": debug_reference_value(rule.max_qualion_level),
                },
                result,
            )

            checks.append(result)

        # Authority
        if rule.min_authority_status_id:
            result = minimum_reference_satisfied(authority, rule.min_authority_status)

            print_condition_debug(
                "authority_status",
                debug_reference_value(authority),
                {
                    "minimum": debug_reference_value(rule.min_authority_status),
                },
                result,
            )

            checks.append(result)

        # Credentials
        required_types = list(rule.required_credential_types.all())

        if required_types:
            matching_credentials = get_matching_credentials(rule, professional_scope, credentials)
            result = bool(matching_credentials)

            print_condition_debug(
                "required_credentials",
                {
                    "matching_credentials": [
                        credential.pk for credential in matching_credentials
                    ]
                },
                {
                    "required_types": [
                        debug_reference_value(required_type)
                        for required_type in required_types
                    ],
                    "require_active_credential": rule.require_active_credential,
                    "max_days_to_credential_expiry": rule.max_days_to_credential_expiry,
                },
                result,
            )

            checks.append(result)

    # ========================================================
    # 3. CANDIDATE / MENTOR CLASSIFICATION
    # ========================================================

    elif field_code == CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION:

        print("CALCULATING: CANDIDATE_MENTOR_CLASSIFICATION")

        # Qualion range
        if rule.min_qualion_level_id or rule.max_qualion_level_id:
            actual_value = professional_scope.current_qualion_level

            result = reference_range_satisfied(
                actual_value,
                rule.min_qualion_level,
                rule.max_qualion_level,
            )

            print_condition_debug(
                "current_qualion_level",
                debug_reference_value(actual_value),
                {
                    "min": debug_reference_value(rule.min_qualion_level),
                    "max": debug_reference_value(rule.max_qualion_level),
                },
                result,
            )

            checks.append(result)

        # Authority
        if rule.min_authority_status_id:
            result = minimum_reference_satisfied(authority, rule.min_authority_status)

            print_condition_debug(
                "authority_status",
                debug_reference_value(authority),
                {
                    "minimum": debug_reference_value(rule.min_authority_status),
                },
                result,
            )

            checks.append(result)

        latest_assessment = None

        if rule.min_ethics_independence_score is not None or rule.require_latest_assessment_decision:
            latest_assessment = get_latest_assessment(professional_scope)

        # Ethics score
        if rule.min_ethics_independence_score is not None:
            actual_score = getattr(latest_assessment, "ethics_independence_score", None) if latest_assessment else None
            result = actual_score is not None and actual_score >= rule.min_ethics_independence_score

            print_condition_debug(
                "ethics_independence_score",
                actual_score,
                {
                    "minimum": rule.min_ethics_independence_score,
                },
                result,
            )

            checks.append(result)

        # Assessment decision
        if rule.require_latest_assessment_decision:
            actual_decision = getattr(latest_assessment, "decision", None) if latest_assessment else None
            result = actual_decision == rule.require_latest_assessment_decision

            print_condition_debug(
                "latest_assessment_decision",
                actual_decision,
                rule.require_latest_assessment_decision,
                result,
            )

            checks.append(result)

        # Pending rejection
        if rule.block_if_pending_rejection:
            has_rejection = has_unresolved_reclassification_rejection(profile)
            result = not has_rejection

            print_condition_debug(
                "block_if_pending_rejection",
                {
                    "has_pending_rejection": has_rejection,
                },
                {
                    "must_not_have_pending_rejection": True,
                },
                result,
            )

            checks.append(result)

    # ========================================================
    # FINAL RULE RESULT
    # ========================================================

    if not checks:
        final_result = True
        print("")
        print("No conditions configured in rule.")
        print("Rule treated as DEFAULT/FALLBACK rule.")

    elif rule.match_type == CalculationRule.MatchType.ANY_CONDITION:
        final_result = any(checks)

    else:
        final_result = all(checks)

    print("")
    print("-" * 100)
    print(f"CHECK RESULTS : {checks}")
    print(f"MATCH TYPE    : {rule.match_type}")
    print(f"RULE RESULT   : {'PASSED' if final_result else 'FAILED'}")

    if field_code == CalculatedFieldCode.QUALION_LEVEL:
        print(f"CONCLUDE VALUE: {debug_reference_value(rule.concluded_qualion_level)}")

    elif field_code == CalculatedFieldCode.DEPLOYABILITY_FLAG:
        print(f"CONCLUDE VALUE: {rule.concluded_deployability_status}")

    elif field_code == CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION:
        print(f"CONCLUDE VALUE: {rule.concluded_classification}")

    print("=" * 100)
    print("")

    return final_result
# ============================================================
# FIND FIRST MATCHING RULE
# ============================================================

# def find_matching_rule(rules, professional_scope, profile, credentials):
#     """
#     First matching rule wins.

#     Rules must already be ordered by sequence.
#     """
#     for rule in rules:
#         if evaluate_rule(rule, professional_scope, profile, credentials):
#             return rule

#     return None

def find_matching_rule(rules, professional_scope, profile, credentials):

    print("")
    print("#" * 100)
    print("STARTING RULE SEARCH")
    print("#" * 100)
    print(f"Professional ID : {profile.pk}")
    print(f"Scope ID        : {professional_scope.scope_id}")
    print(f"Scope           : {professional_scope.scope}")
    print(f"Rules Found     : {len(rules)}")

    if not rules:
        print("No rules found for this field/scope.")
        print("#" * 100)
        return None

    for rule in rules:

        print("")
        print(f"Trying Rule ID={rule.pk}, Sequence={rule.sequence}, Label={rule.label}")

        result = evaluate_rule(
            rule,
            professional_scope,
            profile,
            credentials,
        )

        if result:
            print("")
            print(">>> MATCHING RULE FOUND <<<")
            print(f"Rule ID   : {rule.pk}")
            print(f"Sequence  : {rule.sequence}")
            print(f"Label     : {rule.label}")
            print("#" * 100)
            print("")

            return rule

        print(f"Rule ID={rule.pk} FAILED. Checking next rule...")

    print("")
    print(">>> NO MATCHING RULE FOUND <<<")
    print("#" * 100)
    print("")

    return None
# ============================================================
# BEST PROFESSIONAL SCOPE
# ============================================================

def get_best_professional_scope(professional_scopes):
    """
    Used for tenant-wide CANDIDATE_MENTOR_CLASSIFICATION.

    Priority:
        1. current_qualion_level
        2. authority
        3. calendar_experience_months
        4. verified_field_days
    """
    if not professional_scopes:
        return None

    def sort_key(professional_scope):
        qualion_rank = get_reference_rank(professional_scope.current_qualion_level) or 0
        authority_rank = get_reference_rank(get_scope_authority(professional_scope)) or 0
        experience = professional_scope.calendar_experience_months or 0
        field_days = professional_scope.verified_field_days or Decimal("0")

        return qualion_rank, authority_rank, experience, field_days

    return max(professional_scopes, key=sort_key)


# ============================================================
# RESPONSE VALUE HELPERS
# ============================================================

def reference_value_response(reference_value):
    """
    Returns simple API-friendly ReferenceValue information.
    """
    if reference_value is None:
        return None

    return {
        "id": reference_value.pk,
        "code": getattr(reference_value, "code", None),
        "name": getattr(reference_value, "name", None),
        "value": getattr(reference_value, "value", None),
        "sort_order": getattr(reference_value, "sort_order", None),
        "display": str(reference_value),
    }


# ============================================================
# API
# ============================================================

@method_decorator(csrf_exempt, name="dispatch")
class ProfessionalRuleCalculatedFieldsAPIView(APIView):
    """
    Calculates the 3 CalculationRule-driven fields.

    Calculation order:

        1. QUALION_LEVEL
        2. DEPLOYABILITY_FLAG
        3. CANDIDATE_MENTOR_CLASSIFICATION

    Input:
        ProfessionalProfile pk from URL.

    Example:
        POST /professional/rule-calculated-fields/25/

    No request body required.
    """

    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request, pk):

        # ====================================================
        # 1. PROFESSIONAL PROFILE
        # ====================================================

        try:
            profile = ProfessionalProfile.objects.select_for_update().get(pk=pk)
        except ProfessionalProfile.DoesNotExist:
            return Response({"success": False, "message": "ProfessionalProfile not found."}, status=status.HTTP_404_NOT_FOUND)

        # ====================================================
        # 2. PROFESSIONAL SCOPES
        # ====================================================

        professional_scopes = list(ProfessionalScope.objects.select_for_update().filter(professional=profile, tenant=profile.tenant).select_related("scope", "current_qualion_level", "highest_authority_reached"))

        if not professional_scopes:
            return Response({"success": False, "message": "No ProfessionalScope records found. Run the existing 12-field calculated-fields API first.", "professional_profile_id": str(profile.pk)}, status=status.HTTP_400_BAD_REQUEST)

        # ====================================================
        # 3. PROFESSIONAL CREDENTIALS
        # ====================================================

        credentials = list(CredentialRecord.objects.filter(professional=profile, tenant=profile.tenant))

        # ====================================================
        # 4. ACTIVE CALCULATION RULES
        # ====================================================

        all_rules = list(CalculationRule.objects.filter(tenant=profile.tenant, is_active=True, calculation_field_code__in=[CalculatedFieldCode.QUALION_LEVEL, CalculatedFieldCode.DEPLOYABILITY_FLAG, CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION]).select_related("min_qualion_level", "max_qualion_level", "min_authority_status", "min_complexity_rating", "concluded_qualion_level").prefetch_related("scope", "required_credential_types").order_by("calculation_field_code", "sequence"))

        scope_results = []

        # ====================================================
        # 5. QUALION LEVEL
        # ====================================================

        for professional_scope in professional_scopes:

            qualion_rules = [rule for rule in all_rules if rule.calculation_field_code == CalculatedFieldCode.QUALION_LEVEL and rule_applies_to_professional_scope(rule, professional_scope)]

            matched_qualion_rule = find_matching_rule(qualion_rules, professional_scope, profile, credentials)

            previous_qualion = professional_scope.current_qualion_level

            if matched_qualion_rule:
                professional_scope.current_qualion_level = matched_qualion_rule.concluded_qualion_level
                professional_scope.save(update_fields=["current_qualion_level"])

            print("")
            print("*" * 100)
            print("FINAL QUALION LEVEL RESULT")
            print(f"Professional ID : {profile.pk}")
            print(f"Scope ID        : {professional_scope.scope_id}")
            print(f"Scope           : {professional_scope.scope}")
            print(f"Previous Value  : {debug_reference_value(previous_qualion)}")
            print(f"Final Value     : {debug_reference_value(professional_scope.current_qualion_level) if matched_qualion_rule else None}")
            print(f"Matched Rule ID : {matched_qualion_rule.pk if matched_qualion_rule else None}")
            print(f"Matched Rule    : {matched_qualion_rule.label if matched_qualion_rule else None}")
            print("*" * 100)
            scope_results.append({
                "professional_scope_id": str(professional_scope.pk),
                "scope_id": professional_scope.scope_id,
                "scope": getattr(professional_scope.scope, "scope_name", str(professional_scope.scope)),
                "qualion_level": {
                    "previous": reference_value_response(previous_qualion),
                    "calculated": reference_value_response(professional_scope.current_qualion_level) if matched_qualion_rule else None,
                    "matched_rule_id": matched_qualion_rule.pk if matched_qualion_rule else None,
                    "matched_rule": matched_qualion_rule.label if matched_qualion_rule else None,
                    "requires_four_eyes_approval": matched_qualion_rule.requires_four_eyes_approval if matched_qualion_rule else False,
                }
            })

        # ====================================================
        # REFRESH PROFESSIONAL SCOPES
        # Deployability depends on newly calculated Qualion.
        # ====================================================

        professional_scopes = list(ProfessionalScope.objects.filter(professional=profile, tenant=profile.tenant).select_related("scope", "current_qualion_level", "highest_authority_reached"))

        # ====================================================
        # 6. DEPLOYABILITY FLAG
        # ====================================================

        for professional_scope in professional_scopes:

            deployability_rules = [rule for rule in all_rules if rule.calculation_field_code == CalculatedFieldCode.DEPLOYABILITY_FLAG and rule_applies_to_professional_scope(rule, professional_scope)]

            matched_deployability_rule = find_matching_rule(deployability_rules, professional_scope, profile, credentials)

            # previous_status = getattr(professional_scope, "deployability_status", None)

            # if matched_deployability_rule:
            #     professional_scope.deployability_status = matched_deployability_rule.concluded_deployability_status
            #     professional_scope.save(update_fields=["deployability_status"])
            previous_status = professional_scope.is_deployable

            if matched_deployability_rule:
                professional_scope.is_deployable = matched_deployability_rule.concluded_deployability_status
                professional_scope.save(update_fields=["is_deployable"])
                
            print("")
            print("*" * 100)
            print("FINAL DEPLOYABILITY RESULT")
            print(f"Professional ID : {profile.pk}")
            print(f"Scope ID        : {professional_scope.scope_id}")
            print(f"Scope           : {professional_scope.scope}")
            print(f"Previous Value  : {previous_status}")
            print(f"Final Value     : {professional_scope.is_deployable if matched_deployability_rule else None}")
            print(f"Matched Rule ID : {matched_deployability_rule.pk if matched_deployability_rule else None}")
            print(f"Matched Rule    : {matched_deployability_rule.label if matched_deployability_rule else None}")
            print("*" * 100)


            # response_row = next((row for row in scope_results if row["professional_scope_id"] == str(professional_scope.pk)), None)
            response_row = next((row for row in scope_results if row["professional_scope_id"] == str(professional_scope.pk)), None)

            if response_row is not None:
                response_row["deployability"] = {
                    "previous": previous_status,
                    "calculated": professional_scope.is_deployable if matched_deployability_rule else None,
                    "matched_rule_id": matched_deployability_rule.pk if matched_deployability_rule else None,
                    "matched_rule": matched_deployability_rule.label if matched_deployability_rule else None,
                    "requires_four_eyes_approval": matched_deployability_rule.requires_four_eyes_approval if matched_deployability_rule else False,
                }
            
            # if response_row is not None:
                # response_row["deployability"] = {
                #     "previous": previous_status,
                #     "calculated": matched_deployability_rule.concluded_deployability_status if matched_deployability_rule else None,
                #     "matched_rule_id": matched_deployability_rule.pk if matched_deployability_rule else None,
                #     "matched_rule": matched_deployability_rule.label if matched_deployability_rule else None,
                #     "requires_four_eyes_approval": matched_deployability_rule.requires_four_eyes_approval if matched_deployability_rule else False,
                # }
                

        # ====================================================
        # REFRESH AGAIN BEFORE CLASSIFICATION
        # ====================================================

        professional_scopes = list(ProfessionalScope.objects.filter(professional=profile, tenant=profile.tenant).select_related("scope", "current_qualion_level", "highest_authority_reached"))

        # ====================================================
        # 7. BEST PROFESSIONAL SCOPE
        # ====================================================

        best_scope = get_best_professional_scope(professional_scopes)

        # ====================================================
        # 8. CANDIDATE / MENTOR CLASSIFICATION
        # ====================================================

        classification_result = None

        if best_scope:

            tenant_wide_rules = [rule for rule in all_rules if rule.calculation_field_code == CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION and is_tenant_wide_rule(rule)]

            if tenant_wide_rules:
                classification_rules = tenant_wide_rules
            else:
                classification_rules = [rule for rule in all_rules if rule.calculation_field_code == CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION and rule_applies_to_professional_scope(rule, best_scope)]

            matched_classification_rule = find_matching_rule(classification_rules, best_scope, profile, credentials)

            previous_classification = profile.current_classification

            if matched_classification_rule:
                profile.current_classification = matched_classification_rule.concluded_classification
                profile.save(update_fields=["current_classification"])

            print("")
            print("*" * 100)
            print("FINAL CANDIDATE / MENTOR CLASSIFICATION")
            print(f"Professional ID : {profile.pk}")
            print(f"Best Scope ID   : {best_scope.scope_id}")
            print(f"Best Scope      : {best_scope.scope}")
            print(f"Previous Value  : {previous_classification}")
            print(f"Final Value     : {profile.current_classification if matched_classification_rule else None}")
            print(f"Matched Rule ID : {matched_classification_rule.pk if matched_classification_rule else None}")
            print(f"Matched Rule    : {matched_classification_rule.label if matched_classification_rule else None}")
            print("*" * 100)

            classification_result = {
                "best_professional_scope_id": str(best_scope.pk),
                "scope_id": best_scope.scope_id,
                "scope": getattr(best_scope.scope, "scope_name", str(best_scope.scope)),
                "previous": previous_classification,
                "calculated": matched_classification_rule.concluded_classification if matched_classification_rule else None,
                "matched_rule_id": matched_classification_rule.pk if matched_classification_rule else None,
                "matched_rule": matched_classification_rule.label if matched_classification_rule else None,
                "requires_four_eyes_approval": matched_classification_rule.requires_four_eyes_approval if matched_classification_rule else False,
            }

        # ====================================================
        # 9. FINAL RESPONSE
        # ====================================================

        return Response({
            "success": True,
            "message": "Rule-driven system calculated fields calculated successfully.",
            "professional_profile_id": str(profile.pk),
            "scope_results": scope_results,
            "candidate_mentor_classification": classification_result,
        }, status=status.HTTP_200_OK)

             

                      

        