import json

from django.apps import apps
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import *
from catalog.models import *
from competency.models import *
from evidence.models import *
from experience.models import *
from governance.models import *
from professionals.models import *
from resumes.models import *
from tenancy.models import *

from .serializers import *


@method_decorator(csrf_exempt, name="dispatch")
class ProfessionalProfileRelatedRecordsAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        description="Fetch a professional profile and all related user records by ProfessionalProfile primary key.",
        responses={200: CoreProfessionalProfileRelatedSerializer()},
    )
    def get(self, request, pk):
        profile = get_object_or_404(ProfessionalProfile, pk=pk)
        serializer = CoreProfessionalProfileRelatedSerializer(profile)
        return Response(
            {
                "success": True,
                "message": "Professional profile related records fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class GlobalDynamicTableFilterAPIView(APIView):
    permission_classes = [AllowAny]

    def _resolve_model(self, table_name):
        if not table_name:
            return None

        normalized = str(table_name).strip()
        if not normalized:
            return None

        lookup_values = {
            normalized,
            normalized.lower(),
            normalized.replace("-", "_").replace(" ", "_"),
        }

        for model in apps.get_models():
            names = {
                model.__name__,
                model.__name__.lower(),
                model._meta.model_name,
                model._meta.model_name.lower(),
                model._meta.label_lower,
                model._meta.label_lower.lower(),
                model._meta.db_table,
                (model._meta.db_table or "").lower(),
            }
            if names.intersection(lookup_values):
                return model
        return None

    def _normalize_filters(self, filters_dict):
        if not filters_dict:
            return {}

        if not isinstance(filters_dict, dict):
            return {}

        normalized = {}
        for key, value in filters_dict.items():
            if key is None:
                continue
            field_name = str(key).strip()
            if not field_name:
                continue
            normalized[field_name] = value
        return normalized

    def _get_filter_section(self, item, section_names):
        for key in section_names:
            value = item.get(key)
            if value not in (None, {}, [], ""):
                return value
        return {}

    def _get_return_fields(self, item):
        raw_fields = item.get("return_fields")
        if raw_fields in (None, "", [], ()): 
            return []
        if isinstance(raw_fields, str):
            raw_fields = [raw_fields]
        return [str(field).strip() for field in raw_fields if str(field).strip()]

    def _build_filter_kwargs(self, field, value):
        if isinstance(value, dict):
            q = Q()
            for operator, operator_value in value.items():
                op = str(operator).lower()
                if op == "exact":
                    q &= Q(**{field: operator_value})
                elif op in {"gt", "gte", "lt", "lte"}:
                    q &= Q(**{f"{field}__{op}": operator_value})
                elif op == "in":
                    q &= Q(**{f"{field}__in": operator_value})
                elif op == "contains":
                    q &= Q(**{f"{field}__icontains": operator_value})
                elif op == "startswith":
                    q &= Q(**{f"{field}__startswith": operator_value})
                elif op == "endswith":
                    q &= Q(**{f"{field}__endswith": operator_value})
                elif op == "isnull":
                    q &= Q(**{f"{field}__isnull": bool(operator_value)})
            return q
        if isinstance(value, (list, tuple, set)):
            return Q(**{f"{field}__in": list(value)})
        return Q(**{field: value})

    def _apply_query(self, queryset, filters_dict, mode="include"):
        if not filters_dict:
            return queryset

        query = Q()
        for key, value in filters_dict.items():
            # Convert dot notation to Django's double-underscore notation
            # e.g., "professional.user.is_candidate" -> "professional__user__is_candidate"
            django_key = key.replace(".", "__")
            
            # Try to validate the field path by splitting and checking
            field_parts = django_key.split("__")
            model = queryset.model
            field_valid = True
            
            for part in field_parts:
                if hasattr(model, part):
                    field_obj = getattr(model, part)
                    # If it's a relation, get the related model
                    if hasattr(field_obj, "related_model"):
                        model = field_obj.related_model
                    elif hasattr(field_obj, "field") and hasattr(field_obj.field, "related_model"):
                        model = field_obj.field.related_model
                else:
                    field_valid = False
                    break
            
            if not field_valid:
                continue
            
            if mode == "include":
                query &= self._build_filter_kwargs(django_key, value)
            else:
                query &= ~self._build_filter_kwargs(django_key, value)
        
        if mode == "include":
            return queryset.filter(query)
        return queryset.filter(~query)

    def _parse_payload(self, data):
        if isinstance(data, list):
            return data

        if isinstance(data, dict) and "tables" in data:
            return data["tables"]

        if isinstance(data, str):
            try:
                parsed = json.loads(data)
                if isinstance(parsed, list):
                    return parsed
                if isinstance(parsed, dict) and "tables" in parsed:
                    return parsed["tables"]
            except (TypeError, ValueError):
                return []

        return []

    @extend_schema(
        description="Run a single combined global query across multiple models using includes/excludes and allowed output fields.",
        request=DynamicTableQueryListSerializer,
    )
    def post(self, request):
        payload = self._parse_payload(request.data)
        if not payload:
            return Response(
                {"success": False, "message": "Payload must be a non-empty list of table filter objects."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = DynamicTableQueryListSerializer(data=payload)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = []
        for item in serializer.validated_data:
            table_name = item.get("table")
            model = self._resolve_model(table_name)
            if model is None:
                results.append(
                    {
                        "table": table_name,
                        "success": False,
                        "message": "Table/model not found.",
                        "data": [],
                    }
                )
                continue

            includes = self._normalize_filters(self._get_filter_section(item, ["includes", "include"]))
            excludes = self._normalize_filters(self._get_filter_section(item, ["excludes", "exclude"]))
            return_fields = self._get_return_fields(item)

            queryset = model.objects.all()
            queryset = self._apply_query(queryset, includes, mode="include")
            queryset = self._apply_query(queryset, excludes, mode="exclude")

            if return_fields:
                valid_fields = []
                for field_name in return_fields:
                    field = field_name.strip()
                    if not field:
                        continue
                    # Convert dot notation to Django's __ notation for related fields
                    django_field = field.replace(".", "__")
                    
                    # Simple validation: split and check if traversal is possible
                    field_parts = django_field.split("__")
                    check_model = model
                    field_valid = True
                    
                    for part in field_parts:
                        if hasattr(check_model, part):
                            field_obj = getattr(check_model, part)
                            if hasattr(field_obj, "related_model"):
                                check_model = field_obj.related_model
                            elif hasattr(field_obj, "field") and hasattr(field_obj.field, "related_model"):
                                check_model = field_obj.field.related_model
                        else:
                            field_valid = False
                            break
                    
                    if field_valid:
                        valid_fields.append(django_field)
                
                if valid_fields:
                    queryset = queryset.values(*valid_fields)
                else:
                    queryset = queryset.values()
            else:
                queryset = queryset.values()

            results.append(
                {
                    "table": table_name,
                    "success": True,
                    "includes": includes,
                    "excludes": excludes,
                    "return_fields": return_fields,
                    "data": list(queryset),
                }
            )

        return Response({"success": True, "data": results}, status=status.HTTP_200_OK)

    def get(self, request):
        payload = request.query_params.get("payload")
        data = self._parse_payload(payload)
        if not data:
            return Response(
                {"success": False, "message": "Provide a payload list or ?payload=[...] query param."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = DynamicTableQueryListSerializer(data=data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = []
        for item in serializer.validated_data:
            table_name = item.get("table")
            model = self._resolve_model(table_name)
            if model is None:
                results.append(
                    {
                        "table": table_name,
                        "success": False,
                        "message": "Table/model not found.",
                        "data": [],
                    }
                )
                continue

            includes = self._normalize_filters(self._get_filter_section(item, ["includes", "include"]))
            excludes = self._normalize_filters(self._get_filter_section(item, ["excludes", "exclude"]))
            return_fields = self._get_return_fields(item)

            queryset = model.objects.all()
            queryset = self._apply_query(queryset, includes, mode="include")
            queryset = self._apply_query(queryset, excludes, mode="exclude")

            if return_fields:
                valid_fields = []
                for field_name in return_fields:
                    field = field_name.strip()
                    if not field:
                        continue
                    # Convert dot notation to Django's __ notation for related fields
                    django_field = field.replace(".", "__")
                    
                    # Simple validation: split and check if traversal is possible
                    field_parts = django_field.split("__")
                    check_model = model
                    field_valid = True
                    
                    for part in field_parts:
                        if hasattr(check_model, part):
                            field_obj = getattr(check_model, part)
                            if hasattr(field_obj, "related_model"):
                                check_model = field_obj.related_model
                            elif hasattr(field_obj, "field") and hasattr(field_obj.field, "related_model"):
                                check_model = field_obj.field.related_model
                        else:
                            field_valid = False
                            break
                    
                    if field_valid:
                        valid_fields.append(django_field)
                
                if valid_fields:
                    queryset = queryset.values(*valid_fields)
                else:
                    queryset = queryset.values()
            else:
                queryset = queryset.values()

            results.append(
                {
                    "table": table_name,
                    "success": True,
                    "includes": includes,
                    "excludes": excludes,
                    "return_fields": return_fields,
                    "data": list(queryset),
                }
            )

        return Response({"success": True, "data": results}, status=status.HTTP_200_OK)
