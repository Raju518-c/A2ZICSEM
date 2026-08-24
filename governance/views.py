from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import *
from .serializers import *

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

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.models import ScopeCatalog
from governance.models import CalculatedFieldCode, CalculatedFieldOverride
from governance.serializers import CalculatedFieldOverrideSerializer
from .governance_calculation_engine import (
    FIELD_HANDLERS,
    SCOPED_FIELDS,
    CalculationError,
    apply_calculated_value,
)
from professionals.models import ProfessionalProfile


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







