import json

from django.apps import apps
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema, OpenApiResponse
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
from .models import *
from .serializers import *

from .utils import (
    send_tenant_registration_invitation_email,
)


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


@method_decorator(csrf_exempt, name="dispatch")
class TenantRegistrationInviteListCreateAPIView(APIView):
    """
    GET:
        Get all tenant registration invitations.

    POST:
        Create a tenant registration invitation
        and send registration email.

    Frontend POST payload:

    {
        "email": "tenant@example.com",
        "registration_url": "http://localhost:3000/tenant/register/"
    }

    Backend automatically:

    1. Checks whether tenant already exists.
    2. Checks whether an active invitation already exists.
    3. Creates invitation.
    4. Generates invitation token.
    5. Generates tokenized registration URL.
    6. Sends registration email.
    """

    permission_classes = [AllowAny]

    # ======================================================
    # GET - ALL INVITATIONS
    # ======================================================

    @extend_schema(
        responses=TenantRegistrationInviteSerializer
    )
    def get(self, request):

        invites = TenantRegistrationInvite.objects.all()

        serializer = TenantRegistrationInviteSerializer(
            invites,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": (
                    "Tenant registration invitations "
                    "fetched successfully."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # ======================================================
    # POST - CREATE INVITATION
    # ======================================================

    @extend_schema(
        request=TenantRegistrationInviteCreateSerializer,
        responses={
            201: OpenApiResponse(
                description=(
                    "Tenant registration invitation(s) created "
                    "and email(s) sent successfully."
                )
            ),
            207: OpenApiResponse(
                description=(
                    "Some invitations were created successfully "
                    "while others failed."
                )
            ),
            400: OpenApiResponse(
                description="Validation error."
            ),
            500: OpenApiResponse(
                description="Email sending failed."
            ),
        },
    )
    def post(self, request):

        # ==================================================
        # DETECT SINGLE OR MULTIPLE PAYLOAD
        # ==================================================

        is_multiple = isinstance(request.data, list)

        serializer = TenantRegistrationInviteCreateSerializer(
            data=request.data,
            many=is_multiple
        )

        # ==================================================
        # VALIDATE REQUEST
        # ==================================================

        if not serializer.is_valid():

            return Response(
                {
                    "success": False,
                    "message": "Validation failed.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # NORMALIZE DATA INTO LIST
        # ==================================================

        if is_multiple:
            invitation_records = serializer.validated_data
        else:
            invitation_records = [
                serializer.validated_data
            ]

        # ==================================================
        # RESULT COLLECTION
        # ==================================================

        success_records = []
        failed_records = []

        # Used to prevent duplicate email in same payload
        processed_emails = set()

        # ==================================================
        # PROCESS EACH INVITATION
        # ==================================================

        for item in invitation_records:

            email = item["email"].lower().strip()

            registration_base_url = (
                item["registration_url"].rstrip("/")
            )

            description = item.get(
                "description"
            )

            registered_industry = item.get(
                "registered_industry"
            )

            # ==================================================
            # CHECK DUPLICATE EMAIL INSIDE SAME REQUEST
            # ==================================================

            if email in processed_emails:

                failed_records.append(
                    {
                        "email": email,
                        "message": (
                            "Duplicate email found in "
                            "the same request."
                        ),
                    }
                )

                continue

            processed_emails.add(email)

            # ==================================================
            # CHECK IF ALREADY REGISTERED
            # ==================================================

            existing_registered_invite = (
                TenantRegistrationInvite.objects.filter(
                    email__iexact=email,
                    is_registered=True
                )
                .select_related("tenant_rec")
                .order_by("-registered_date_time")
                .first()
            )

            if existing_registered_invite:

                failed_records.append(
                    {
                        "email": email,
                        "message": (
                            "A tenant is already registered "
                            "with this email."
                        ),
                        "tenant_id": (
                            str(
                                existing_registered_invite
                                .tenant_rec_id
                            )
                            if existing_registered_invite
                            .tenant_rec_id
                            else None
                        ),
                        "invite_id": (
                            existing_registered_invite.id
                        ),
                        "is_registered": True,
                        "registered_date_time": (
                            existing_registered_invite
                            .registered_date_time
                        ),
                    }
                )

                continue

            # ==================================================
            # CHECK EXISTING ACTIVE INVITATION
            # ==================================================

            existing_invite = (
                TenantRegistrationInvite.objects.filter(
                    email__iexact=email,
                    is_registered=False
                )
                .order_by("-invitation_date_time")
                .first()
            )

            if existing_invite:

                failed_records.append(
                    {
                        "email": email,
                        "message": (
                            "An active tenant registration "
                            "invitation already exists for "
                            "this email."
                        ),
                        "invite_id": (
                            existing_invite.id
                        ),
                        "is_registered": (
                            existing_invite.is_registered
                        ),
                        "invitation_date_time": (
                            existing_invite
                            .invitation_date_time
                        ),
                        "invitation_token": str(
                            existing_invite
                            .invitation_token
                        ),
                    }
                )

                continue

            # ==================================================
            # CREATE INVITATION
            # ==================================================

            invite = (
                TenantRegistrationInvite.objects.create(
                    email=email,
                    description=description,
                    registered_industry=registered_industry,
                )
            )

            # ==================================================
            # GENERATE TOKENIZED REGISTRATION URL
            # ==================================================

            registration_url = (
                f"{registration_base_url}"
                f"/?token={invite.invitation_token}"
            )

            # ==================================================
            # EMAIL SUBJECT
            # ==================================================

            subject = (
                "Welcome to A2Z - Tenant Registration"
            )

            # ==================================================
            # EMAIL MESSAGE
            # ==================================================

            message = (
                "Hello,\n\n"
                "You have been invited to register as a "
                "tenant on A2Z.\n\n"
                "Please complete your tenant registration "
                "using the link below:\n\n"
                f"{registration_url}\n\n"
                "Please do not share this registration link "
                "with anyone else.\n\n"
                "Thank you,\n"
                "A2Z Team"
            )

            # ==================================================
            # SEND EMAIL
            # ==================================================

            try:

                send_tenant_registration_invitation_email(
                    email=invite.email,
                    subject=subject,
                    message=message,
                )

            except Exception as e:

                # Delete invitation when email sending fails
                invite.delete()

                failed_records.append(
                    {
                        "email": email,
                        "message": (
                            "Failed to send tenant "
                            "registration invitation email."
                        ),
                        "error": str(e),
                    }
                )

                continue

            # ==================================================
            # SUCCESS RECORD
            # ==================================================

            success_records.append(
                {
                    "id": invite.id,
                    "email": invite.email,
                    "description": invite.description,
                    "registered_industry": (
                        invite.registered_industry
                    ),
                    "invitation_date_time": (
                        invite.invitation_date_time
                    ),
                    "is_registered": (
                        invite.is_registered
                    ),
                    "registered_date_time": (
                        invite.registered_date_time
                    ),
                    "tenant_rec": (
                        str(invite.tenant_rec_id)
                        if invite.tenant_rec_id
                        else None
                    ),
                    "invitation_token": str(
                        invite.invitation_token
                    ),
                    "registration_url": (
                        registration_url
                    ),
                    "email_subject": subject,
                    "email_message": message,
                }
            )

        # ==================================================
        # SINGLE RECORD RESPONSE
        # ==================================================

        if not is_multiple:

            if success_records:

                return Response(
                    {
                        "success": True,
                        "message": (
                            "Tenant registration invitation "
                            "created and email sent successfully."
                        ),
                        "data": success_records[0],
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                {
                    "success": False,
                    "message": (
                        failed_records[0].get(
                            "message",
                            "Failed to create invitation."
                        )
                    ),
                    "data": failed_records[0],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # MULTIPLE RECORD RESPONSE
        # ==================================================

        total_records = len(invitation_records)
        success_count = len(success_records)
        failed_count = len(failed_records)

        # --------------------------------------------------
        # ALL SUCCESS
        # --------------------------------------------------

        if failed_count == 0:

            return Response(
                {
                    "success": True,
                    "message": (
                        "All tenant registration invitations "
                        "were created and emails sent "
                        "successfully."
                    ),
                    "summary": {
                        "total": total_records,
                        "success": success_count,
                        "failed": failed_count,
                    },
                    "data": {
                        "successful": success_records,
                        "failed": [],
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        # --------------------------------------------------
        # ALL FAILED
        # --------------------------------------------------

        if success_count == 0:

            return Response(
                {
                    "success": False,
                    "message": (
                        "No tenant registration invitations "
                        "were created."
                    ),
                    "summary": {
                        "total": total_records,
                        "success": success_count,
                        "failed": failed_count,
                    },
                    "data": {
                        "successful": [],
                        "failed": failed_records,
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # PARTIAL SUCCESS
        # --------------------------------------------------

        return Response(
            {
                "success": True,
                "partial_success": True,
                "message": (
                    "Some tenant registration invitations "
                    "were created successfully while "
                    "others failed."
                ),
                "summary": {
                    "total": total_records,
                    "success": success_count,
                    "failed": failed_count,
                },
                "data": {
                    "successful": success_records,
                    "failed": failed_records,
                },
            },
            status=status.HTTP_207_MULTI_STATUS,
        )

@method_decorator(csrf_exempt, name="dispatch")
class TenantRegistrationInviteDetailAPIView(APIView):
    """
    GET    : Get one tenant registration invitation
    PUT    : Update invitation email
    PATCH  : Partially update invitation email
    DELETE : Delete invitation
    """

    permission_classes = [AllowAny]

    # ======================================================
    # GET
    # ======================================================

    @extend_schema(
        responses=TenantRegistrationInviteSerializer
    )
    def get(self, request, pk):

        invite = get_object_or_404(
            TenantRegistrationInvite,
            pk=pk
        )

        serializer = TenantRegistrationInviteSerializer(
            invite
        )

        return Response(
            {
                "success": True,
                "message": (
                    "Tenant registration invitation "
                    "fetched successfully."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # ======================================================
    # PUT
    # ======================================================

    @extend_schema(
        request=TenantRegistrationInviteCreateSerializer,
        responses=TenantRegistrationInviteSerializer,
    )
    def put(self, request, pk):

        invite = get_object_or_404(
            TenantRegistrationInvite,
            pk=pk
        )

        serializer = TenantRegistrationInviteCreateSerializer(
            invite,
            data=request.data
        )

        if not serializer.is_valid():

            return Response(
                {
                    "success": False,
                    "message": "Validation failed.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        invite = serializer.save()

        return Response(
            {
                "success": True,
                "message": (
                    "Tenant registration invitation "
                    "updated successfully."
                ),
                "data": TenantRegistrationInviteSerializer(
                    invite
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    # ======================================================
    # PATCH
    # ======================================================

    @extend_schema(
        request=TenantRegistrationInviteCreateSerializer,
        responses=TenantRegistrationInviteSerializer,
    )
    def patch(self, request, pk):

        invite = get_object_or_404(
            TenantRegistrationInvite,
            pk=pk
        )

        serializer = TenantRegistrationInviteCreateSerializer(
            invite,
            data=request.data,
            partial=True
        )

        if not serializer.is_valid():

            return Response(
                {
                    "success": False,
                    "message": "Validation failed.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        invite = serializer.save()

        return Response(
            {
                "success": True,
                "message": (
                    "Tenant registration invitation "
                    "updated successfully."
                ),
                "data": TenantRegistrationInviteSerializer(
                    invite
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    # ======================================================
    # DELETE
    # ======================================================

    @extend_schema(
        responses={
            204: OpenApiResponse(
                description=(
                    "Tenant registration invitation "
                    "deleted successfully."
                )
            )
        }
    )
    def delete(self, request, pk):

        invite = get_object_or_404(
            TenantRegistrationInvite,
            pk=pk
        )

        invite.delete()

        return Response(
            {
                "success": True,
                "message": (
                    "Tenant registration invitation "
                    "deleted successfully."
                ),
            },
            status=status.HTTP_204_NO_CONTENT,
        )


@method_decorator(csrf_exempt, name="dispatch")
class TenantRegistrationInviteByTokenAPIView(APIView):
    """
    GET:
        Validate tenant registration invitation using token.

    If invitation is NOT registered:
        Return registration URL.

    If invitation is already registered:
        Return the registered Tenant record.

    URL:
        GET /tenant-registration-invite/<token>/
    """

    permission_classes = [AllowAny]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description=(
                    "Invitation token validated successfully."
                )
            ),
            404: OpenApiResponse(
                description="Invalid invitation token."
            ),
        }
    )
    def get(self, request, token):

        # ==================================================
        # FIND INVITATION BY TOKEN
        # ==================================================

        invite = (
            TenantRegistrationInvite.objects
            .select_related("tenant_rec")
            .filter(
                invitation_token=token
            )
            .first()
        )

        # ==================================================
        # INVALID TOKEN
        # ==================================================

        if not invite:

            return Response(
                {
                    "success": False,
                    "message": (
                        "no tenant registration invitation."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # ==================================================
        # ALREADY REGISTERED
        # ==================================================

        if invite.is_registered:

            # ----------------------------------------------
            # Check whether tenant is linked
            # ----------------------------------------------

            if not invite.tenant_rec:

                return Response(
                    {
                        "success": False,
                        "message": (
                            "This invitation is already "
                            "registered, but the associated "
                            "tenant record was not found."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tenant = invite.tenant_rec

            # ----------------------------------------------
            # Return registered tenant
            # ----------------------------------------------

            return Response(
                {
                    "success": True,
                    "message": (
                        "Tenant registration is already "
                        "completed."
                    ),
                    "registered": True,
                    "data": {
                        "invitation": {
                            "id": invite.id,
                            "email": invite.email,
                            "is_registered": (
                                invite.is_registered
                            ),
                            "registered_date_time": (
                                invite.registered_date_time
                            ),
                            "invitation_token": str(
                                invite.invitation_token
                            ),
                        },
                        "tenant": {
                            "id": str(tenant.id),
                            "name": tenant.name,
                            "code": tenant.code,
                            "workspace_type": (
                                tenant.workspace_type
                            ),
                            "legal_name": tenant.legal_name,
                            "trade_name": tenant.trade_name,
                            "organisation_type": (
                                tenant.organisation_type
                            ),
                            "description": tenant.description,
                            "website": tenant.website,
                            "industry_ids": tenant.industry_ids,
                            "service_scope_ids": (
                                tenant.service_scope_ids
                            ),
                            "portal_slug": tenant.portal_slug,
                            "custom_domain": (
                                tenant.custom_domain
                            ),
                            "status": tenant.status,
                            "registration_enabled": (
                                tenant.registration_enabled
                            ),
                            "login_enabled": (
                                tenant.login_enabled
                            ),
                            "default_timezone": (
                                tenant.default_timezone
                            ),
                            "default_currency": (
                                tenant.default_currency
                            ),
                            "contact_email": (
                                tenant.contact_email
                            ),
                            "contact_phone": (
                                tenant.contact_phone
                            ),
                            "settings": tenant.settings,
                            "branding": tenant.branding,
                            "logo": (
                                tenant.logo.url
                                if tenant.logo
                                else None
                            ),
                            "status_reason": (
                                tenant.status_reason
                            ),
                            "created_by": (
                                str(tenant.created_by_id)
                                if tenant.created_by_id
                                else None
                            ),
                            "created_at": (
                                tenant.created_at
                            ),
                            "updated_at": (
                                tenant.updated_at
                            ),
                        },
                    },
                },
                status=status.HTTP_200_OK,
            )

        # ==================================================
        # NOT REGISTERED
        # ==================================================

        # Build registration URL
        #
        # This should be the same base URL used when
        # creating the invitation.

        # If you want the frontend URL to be stored in the
        # invitation table, add a registration_url field.
        #
        # Otherwise, use your configured frontend URL.

        # registration_base_url = (
        #     "http://localhost:3000/tenant/register/"
        # )

        # registration_url = (
        #     f"{registration_base_url}"
        #     f"?token={invite.invitation_token}"
        # )

        # ==================================================
        # RETURN REGISTRATION URL
        # ==================================================

        return Response(
            {
                "success": True,
                "message": (
                    "Tenant registration invitation "
                    "is valid."
                ),
                "registered": False,
                "data": {
                    "invite_id": invite.id,
                    "email": invite.email,
                    "is_registered": (
                        invite.is_registered
                    ),                   
                    "invitation_token": str(
                        invite.invitation_token
                    ),
                },
            },
            status=status.HTTP_200_OK,
        )


