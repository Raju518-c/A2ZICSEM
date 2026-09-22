from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiRequest,
    PolymorphicProxySerializer,
    extend_schema,
    inline_serializer,
    OpenApiTypes,
)
from rest_framework import serializers
from rest_framework import parsers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import *
from .serializers import *
from django.utils import timezone
from django.db import transaction
from accounts.models import UserTbl, roles
import uuid
import json
from catalog.models import *

def _request_example(serializer_class):
    example = {}
    serializer = serializer_class()
    for name, field in serializer.fields.items():
        if field.read_only:
            continue
        field_type = field.__class__.__name__
        if field_type == "BooleanField":
            value = False
        elif field_type in {"IntegerField", "DecimalField", "FloatField"}:
            value = 0
        elif field_type == "DateField":
            value = "2026-01-01"
        elif field_type == "DateTimeField":
            value = "2026-01-01T00:00:00Z"
        elif field_type in {"ListField", "DictField", "JSONField"}:
            value = [] if field_type == "ListField" else {}
        elif field_type == "PrimaryKeyRelatedField":
            value = str(uuid.UUID(int=0)) if field.pk_field.__class__.__name__ == "UUIDField" else 1
        elif field_type == "ManyRelatedField":
            value = []
        elif field_type in {"EmailField", "URLField"}:
            value = "user@example.com" if field_type == "EmailField" else "https://example.com"
        elif field_type in {"FileField", "ImageField"}:
            value = "example.pdf" if field_type == "FileField" else "logo.png"
        elif getattr(field, "choices", None):
            value = next(iter(field.choices))
        else:
            value = "string"
        example[name] = value
    return example


def _single_or_bulk_schema(serializer_class):
    schema = PolymorphicProxySerializer(
            component_name=f"{serializer_class.__name__}SingleOrBulk",
            serializers=[serializer_class, serializer_class(many=True)],
            resource_type_field_name=None,
            many=False,
    )
    return OpenApiRequest(
        request=schema,
        examples=[
            OpenApiExample(
                "Single record",
                value=_request_example(serializer_class),
                request_only=True,
            ),
            OpenApiExample(
                "Bulk records",
                value=[_request_example(serializer_class)],
                request_only=True,
            ),
        ],
    )


def _create_serializer(serializer_class, request, tenant_owned=False):
    """Build a serializer for either one object or a list of objects."""
    payload = request.data
    if isinstance(payload, list):
        data = [item.copy() for item in payload]
        if tenant_owned:
            tenant = resolve_tenant(request)
            for item in data:
                if tenant is not None:
                    item["tenant"] = tenant
        return serializer_class(data=data, many=True)

    data = payload.copy()
    if tenant_owned:
        tenant = resolve_tenant(request)
        if tenant is not None:
            data["tenant"] = tenant
    return serializer_class(data=data)


@method_decorator(csrf_exempt, name='dispatch')
class TenantCombinedCreateAPIView(APIView):
    """
    POST : Create a tenant, its operating industries, a tenant admin role,
    and the first tenant admin user in one transaction.
    """

    permission_classes = [AllowAny]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    @extend_schema(request={"multipart/form-data": TenantCombinedCreateSerializer})
    def post(self, request):
        print('request.data', request.data)
        serializer = TenantCombinedCreateSerializer(
            data=request.data,
            context={"files": request.FILES},
        )

        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_data = serializer.save()

        return Response(
            {
                "success": True,
                "message": "Tenant, operations, role and admin user created successfully.",
                "data": {
                    "tenant": TenantSerializer(created_data["tenant"]).data,
                    "operations": TenantOperationSerializer(
                        created_data["operations"], many=True
                    ).data,
                    "role": {
                        "code": created_data["role"].code,
                        "name": created_data["role"].name,
                        "roles_for": created_data["role"].roles_for,
                    },
                    "user": {
                        "id": str(created_data["user"].public_id),
                        "email": created_data["user"].email,
                        "tenant_id": created_data["tenant"].pk,
                    },
                },
            },
            status=status.HTTP_201_CREATED,
        )
            



@method_decorator(csrf_exempt, name='dispatch')
class TenantListCreateAPIView(APIView):
    """
    GET  : Get all tenants
    POST : Create a new tenant
    """

    permission_classes = [AllowAny]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get(self, request):
        tenants = Tenant.objects.all().order_by("name")
        serializer = TenantSerializer(tenants, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenants fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request={"multipart/form-data": TenantSerializer})
    def post(self, request):
        serializer = TenantSerializer(data=request.data)

        if serializer.is_valid():
            tenant_rec = serializer.save()
            
            invitation_token = request.data.get(
                "invitation_token"
            )
            if not invitation_token:        
                return Response(
                    {
                        "success": False,
                        "message": (
                            "Invitation token is required."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            invite = (TenantRegistrationInvite.objects.filter(invitation_token=invitation_token, is_registered=False).first())
            if not invite:
                return Response(
                    {
                        "success": False,
                        "message": (
                            "Invalid or already used "
                            "tenant registration invitation."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            invite.tenant_rec = tenant_rec
            invite.is_registered = True
            invite.registered_date_time = timezone.now()
            invite.save(
                update_fields=[
                    "tenant_rec",
                    "is_registered",
                    "registered_date_time",
                    "updated_at",
                ]
            )
            
            return Response(
                {
                    "success": True,
                    "message": "Tenant created successfully.",
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
class TenantResolveByHostAPIView(APIView):
    """Resolve the current tenant from the request host."""

    permission_classes = [AllowAny]

    def get(self, request):
        host = request.get_host().split(":")[0].strip().lower()
        print('TenantResolveByHostAPIView GET', host)
        if not host:
            return Response(
                {"success": False, "message": "Tenant host not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tenant_slug = host.split(".")[0]
        if tenant_slug in {"localhost", "127", "127.0.0.1", "", "www"}:
            return Response(
                {"success": False, "message": "Tenant host not detected."},
                status=status.HTTP_404_NOT_FOUND,
            )

        tenant = Tenant.objects.filter(
            Q(portal_slug=tenant_slug) | Q(custom_domain__iexact=host)
        ).first()

        if not tenant:
            return Response(
                {"success": False, "message": "Tenant not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantSerializer(tenant)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant created successfully.",
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
class TenantRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Get tenant by ID
    PUT    : Update tenant (partial)
    DELETE : Delete tenant
    """

    permission_classes = [AllowAny]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_object(self, pk):
        try:
            return Tenant.objects.get(pk=pk)
        except Tenant.DoesNotExist:
            return None

    def get(self, request, pk):
        tenant = self.get_object(pk)

        if not tenant:
            return Response(
                {
                    "success": False,
                    "message": "Tenant not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantSerializer(tenant)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request={"multipart/form-data": TenantSerializer})
    def put(self, request, pk):
        tenant = self.get_object(pk)

        if not tenant:
            return Response(
                {
                    "success": False,
                    "message": "Tenant not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantSerializer(tenant, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant updated successfully.",
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
        tenant = self.get_object(pk)

        if not tenant:
            return Response(
                {
                    "success": False,
                    "message": "Tenant not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        tenant.delete()

        return Response(
            {
                "success": True,
                "message": "Tenant deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )

@method_decorator(csrf_exempt, name='dispatch')
class TenantOperationListCreateAPIView(APIView):
    """
    GET  : Get all tenant operations
    POST : Create a new tenant operation
    """

    permission_classes = [AllowAny]

    def get(self, request):
        operations = TenantOperation.objects.all().order_by(
            "tenant", "industry", "country_code"
        )
        serializer = TenantOperationSerializer(operations, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant operations fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=_single_or_bulk_schema(TenantOperationSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantOperationSerializer, request)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant operation created successfully.",
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
class TenantOperationRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Get tenant operation by ID
    PUT    : Update tenant operation (partial)
    DELETE : Delete tenant operation
    """

    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantOperation.objects.get(pk=pk)
        except TenantOperation.DoesNotExist:
            return None

    def get(self, request, pk):
        operation = self.get_object(pk)

        if not operation:
            return Response(
                {
                    "success": False,
                    "message": "Tenant operation not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantOperationSerializer(operation)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=TenantOperationSerializer)
    def put(self, request, pk):
        operation = self.get_object(pk)

        if not operation:
            return Response(
                {
                    "success": False,
                    "message": "Tenant operation not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantOperationSerializer(operation, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant operation updated successfully.",
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
        operation = self.get_object(pk)

        if not operation:
            return Response(
                {
                    "success": False,
                    "message": "Tenant operation not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        operation.delete()

        return Response(
            {
                "success": True,
                "message": "Tenant operation deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )



@method_decorator(csrf_exempt, name='dispatch')
class OrganizationListCreateAPIView(APIView): 
    """
    GET  : Get all organizations
    POST : Create a new organization
    """
    permission_classes = [AllowAny]
    def get(self, request):
        organizations = Organization.objects.all().order_by(
            "tenant",
            "name"
        )

        serializer = OrganizationSerializer(
            organizations,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": "Organizations fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(OrganizationSerializer))
    def post(self, request):
        serializer = _create_serializer(OrganizationSerializer, request)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Organization created successfully.",
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
class OrganizationRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Retrieve organization by ID
    PUT    : Update organization
    DELETE : Delete organization
    """
    permission_classes = [AllowAny]
    def get_object(self, pk):
        try:
            return Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            return None

    def get(self, request, pk):
        organization = self.get_object(pk)

        if not organization:
            return Response(
                {
                    "success": False,
                    "message": "Organization not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrganizationSerializer(organization)

        return Response(
            {
                "success": True,
                "message": "Organization retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=OrganizationSerializer)
    def put(self, request, pk):
        organization = self.get_object(pk)

        if not organization:
            return Response(
                {
                    "success": False,
                    "message": "Organization not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrganizationSerializer(
            organization,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Organization updated successfully.",
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
        organization = self.get_object(pk)

        if not organization:
            return Response(
                {
                    "success": False,
                    "message": "Organization not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        organization.delete()

        return Response(
            {
                "success": True,
                "message": "Organization deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )
        

def resolve_tenant(request):
    """
    TenantOwnedModel.tenant is documented as server-derived and never
    trusted from client payload. Plug in the real resolution here
    (e.g. request.user.tenant, request.tenant set by middleware, etc).
    Raising/returning None left as a placeholder until that's wired up.
    """
    return getattr(request, "tenant", None)


# Only models in this allowlist can be requested by the tenant aggregate API.
# The queryset in each entry is scoped to the supplied tenant before serialization.
TENANT_RECORD_TABLES = {
    "tenant": (Tenant, TenantSerializer, lambda tenant_id: Tenant.objects.filter(pk=tenant_id)),
    "tenant_operations": (TenantOperation, TenantOperationSerializer, lambda tenant_id: TenantOperation.objects.filter(tenant_id=tenant_id)),
    "organizations": (Organization, OrganizationSerializer, lambda tenant_id: Organization.objects.filter(tenant_id=tenant_id)),
    "tenant_legal_entities": (TenantLegalEntity, TenantLegalEntitySerializer, lambda tenant_id: TenantLegalEntity.objects.filter(tenant_id=tenant_id)),
    "tenant_tax_registrations": (TenantTaxRegistration, TenantTaxRegistrationSerializer, lambda tenant_id: TenantTaxRegistration.objects.filter(tenant_id=tenant_id)),
    "tenant_domains": (TenantDomain, TenantDomainSerializer, lambda tenant_id: TenantDomain.objects.filter(tenant_id=tenant_id)),
    "tenant_locations": (TenantLocation, TenantLocationSerializer, lambda tenant_id: TenantLocation.objects.filter(tenant_id=tenant_id)),
    "tenant_authorised_representatives": (TenantAuthorisedRepresentative, TenantAuthorisedRepresentativeSerializer, lambda tenant_id: TenantAuthorisedRepresentative.objects.filter(tenant_id=tenant_id)),
    "tenant_contacts": (TenantContact, TenantContactSerializer, lambda tenant_id: TenantContact.objects.filter(tenant_id=tenant_id)),
    "tenant_verifications": (TenantVerification, TenantVerificationSerializer, lambda tenant_id: TenantVerification.objects.filter(tenant_id=tenant_id)),
    "tenant_documents": (TenantDocument, TenantDocumentSerializer, lambda tenant_id: TenantDocument.objects.filter(tenant_id=tenant_id)),
    "tenant_legal_acceptances": (TenantLegalAcceptance, TenantLegalAcceptanceSerializer, lambda tenant_id: TenantLegalAcceptance.objects.filter(tenant_id=tenant_id)),
    "tenant_legal_settings": (TenantLegalSettings, TenantLegalSettingsSerializer, lambda tenant_id: TenantLegalSettings.objects.filter(tenant_id=tenant_id)),
    "tenant_ndas": (TenantNda, TenantNdaSerializer, lambda tenant_id: TenantNda.objects.filter(tenant_id=tenant_id)),
    "tenant_settings": (TenantSettings, TenantSettingsSerializer, lambda tenant_id: TenantSettings.objects.filter(tenant_id=tenant_id)),
    "tenant_subscriptions": (TenantSubscription, TenantSubscriptionSerializer, lambda tenant_id: TenantSubscription.objects.filter(tenant_id=tenant_id)),
    "tenant_module_entitlements": (TenantModuleEntitlement, TenantModuleEntitlementSerializer, lambda tenant_id: TenantModuleEntitlement.objects.filter(tenant_id=tenant_id)),
    "tenant_brandings": (TenantBranding, TenantBrandingSerializer, lambda tenant_id: TenantBranding.objects.filter(tenant_id=tenant_id)),
    "tenant_report_templates": (TenantReportTemplate, TenantReportTemplateSerializer, lambda tenant_id: TenantReportTemplate.objects.filter(tenant_id=tenant_id)),
    "tenant_security_settings": (TenantSecuritySettings, TenantSecuritySettingsSerializer, lambda tenant_id: TenantSecuritySettings.objects.filter(tenant_id=tenant_id)),
    "tenant_ip_restrictions": (TenantIPRestriction, TenantIPRestrictionSerializer, lambda tenant_id: TenantIPRestriction.objects.filter(security_settings__tenant_id=tenant_id)),
    "tenant_integrations": (TenantIntegration, TenantIntegrationSerializer, lambda tenant_id: TenantIntegration.objects.filter(tenant_id=tenant_id)),
    "tenant_billings": (TenantBilling, TenantBillingSerializer, lambda tenant_id: TenantBilling.objects.filter(tenant_id=tenant_id)),
    "tenant_role_assignments": (TenantRoleAssignment, TenantRoleAssignmentSerializer, lambda tenant_id: TenantRoleAssignment.objects.filter(user__tenant_id=tenant_id)),
    "tenant_invitations": (TenantInvitation, TenantInvitationSerializer, lambda tenant_id: TenantInvitation.objects.filter(tenant_id=tenant_id)),
    "tenant_workflows": (TenantWorkflow, TenantWorkflowSerializer, lambda tenant_id: TenantWorkflow.objects.filter(tenant_id=tenant_id)),
    "tenant_workflow_steps": (TenantWorkflowStep, TenantWorkflowStepSerializer, lambda tenant_id: TenantWorkflowStep.objects.filter(workflow__tenant_id=tenant_id)),
    "tenant_operation_logs": (TenantOperationLog, TenantOperationLogSerializer, lambda tenant_id: TenantOperationLog.objects.filter(tenant_id=tenant_id)),
    "tenant_terminology": (TenantTerminology, TenantTerminologySerializer, lambda tenant_id: TenantTerminology.objects.filter(tenant_id=tenant_id)),
    "tenant_numbering_configs": (TenantNumberingConfig, TenantNumberingConfigSerializer, lambda tenant_id: TenantNumberingConfig.objects.filter(tenant_id=tenant_id)),
    "tenant_approval_matrices": (TenantApprovalMatrix, TenantApprovalMatrixSerializer, lambda tenant_id: TenantApprovalMatrix.objects.filter(tenant_id=tenant_id)),
    "tenant_notification_settings": (TenantNotificationSettings, TenantNotificationSettingsSerializer, lambda tenant_id: TenantNotificationSettings.objects.filter(tenant_id=tenant_id)),
    "conflict_of_interest_declarations": (ConflictOfInterestDeclaration, ConflictOfInterestDeclarationSerializer, lambda tenant_id: ConflictOfInterestDeclaration.objects.filter(tenant_id=tenant_id)),
    "data_export_requests": (DataExportRequest, DataExportRequestSerializer, lambda tenant_id: DataExportRequest.objects.filter(tenant_id=tenant_id)),
    "projects": (Project, ProjectSerializer, lambda tenant_id: Project.objects.filter(tenant_id=tenant_id)),
    "project_memberships": (ProjectMembership, ProjectMembershipSerializer, lambda tenant_id: ProjectMembership.objects.filter(project__tenant_id=tenant_id)),
    "project_requirements": (ProjectRequirement, ProjectRequirementSerializer, lambda tenant_id: ProjectRequirement.objects.filter(project__tenant_id=tenant_id)),
    "project_requirement_scopes": (ProjectRequirementScope, ProjectRequirementScopeSerializer, lambda tenant_id: ProjectRequirementScope.objects.filter(requirement__project__tenant_id=tenant_id)),
    "project_candidates": (ProjectCandidate, ProjectCandidateSerializer, lambda tenant_id: ProjectCandidate.objects.filter(project__tenant_id=tenant_id)),
    "disclosure_requests": (DisclosureRequest, DisclosureRequestSerializer, lambda tenant_id: DisclosureRequest.objects.filter(tenant_id=tenant_id)),
    "candidate_consents": (CandidateConsent, CandidateConsentSerializer, lambda tenant_id: CandidateConsent.objects.filter(disclosure_request__tenant_id=tenant_id)),
    "project_placements": (ProjectPlacement, ProjectPlacementSerializer, lambda tenant_id: ProjectPlacement.objects.filter(project__tenant_id=tenant_id)),
    "project_scope_links": (ProjectScopeLink, ProjectScopeLinkSerializer, lambda tenant_id: ProjectScopeLink.objects.filter(project__tenant_id=tenant_id)),
    "users": (UserTbl, UserTblserializers, lambda tenant_id: UserTbl.objects.filter(tenant_id=tenant_id)),
    "roles": (roles, rolesserializers, lambda tenant_id: roles.objects.filter(tenant_id=tenant_id)),
}


@method_decorator(csrf_exempt, name="dispatch")
class TenantRecordsAPIView(APIView):
    """Return selected tenant and tenant-owned child tables in one response."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Accept tenant_id and tables as a JSON request body."""
        return self.get(request)

    def _tables_from_request(self, request):
        raw_tables = request.query_params.getlist("tables")
        if not raw_tables and getattr(request, "data", None):
            raw_tables = request.data.get("tables", [])
        if isinstance(raw_tables, str):
            raw_tables = raw_tables.strip()
            try:
                raw_tables = json.loads(raw_tables)
            except json.JSONDecodeError:
                raw_tables = raw_tables.split(",")
        if not isinstance(raw_tables, (list, tuple)):
            return []
        return [str(table).strip() for table in raw_tables if str(table).strip()]

    def get(self, request):
        tenant_id = request.query_params.get("tenant_id")
        if tenant_id is None and getattr(request, "data", None):
            tenant_id = request.data.get("tenant_id")

        if not tenant_id:
            return Response(
                {"success": False, "message": "tenant_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            tenant = Tenant.objects.get(pk=tenant_id)
        except (Tenant.DoesNotExist, ValueError, TypeError):
            return Response(
                {"success": False, "message": "Tenant not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        table_names = self._tables_from_request(request)
        if not table_names:
            return Response(
                {"success": False, "message": "tables must be a non-empty list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        unknown_tables = sorted(set(table_names) - set(TENANT_RECORD_TABLES))
        if unknown_tables:
            return Response(
                {
                    "success": False,
                    "message": "Unknown table name(s).",
                    "unknown_tables": unknown_tables,
                    "available_tables": sorted(TENANT_RECORD_TABLES),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = {}
        for table_name in dict.fromkeys(table_names):
            _, serializer_class, queryset_factory = TENANT_RECORD_TABLES[table_name]
            queryset = queryset_factory(tenant.pk)
            data[table_name] = serializer_class(
                queryset if hasattr(queryset, "model") else queryset.first(),
                many=hasattr(queryset, "model"),
            ).data

        return Response(
            {"success": True, "tenant_id": tenant.pk, "data": data},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantLegalEntity
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantLegalEntityListCreateAPIView(APIView):
    """
    GET  : Get all tenant legal entities
    POST : Create a new tenant legal entity
    """

    permission_classes = [AllowAny]

    def get(self, request):
        entities = TenantLegalEntity.objects.all().order_by("-created_at")
        serializer = TenantLegalEntitySerializer(entities, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant legal entities fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantLegalEntitySerializer))
    def post(self, request):
        serializer = _create_serializer(TenantLegalEntitySerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant legal entity created successfully.",
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
class TenantLegalEntityRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Get tenant legal entity by pk
    PUT    : Update tenant legal entity (partial)
    DELETE : Delete tenant legal entity
    """

    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantLegalEntity.objects.get(pk=pk)
        except TenantLegalEntity.DoesNotExist:
            return None

    def get(self, request, pk):
        entity = self.get_object(pk)

        if not entity:
            return Response(
                {
                    "success": False,
                    "message": "Tenant legal entity not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantLegalEntitySerializer(entity)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=TenantLegalEntitySerializer)
    def put(self, request, pk):
        entity = self.get_object(pk)

        if not entity:
            return Response(
                {
                    "success": False,
                    "message": "Tenant legal entity not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)  # tenant is immutable post-creation via this endpoint

        serializer = TenantLegalEntitySerializer(entity, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant legal entity updated successfully.",
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
        entity = self.get_object(pk)

        if not entity:
            return Response(
                {
                    "success": False,
                    "message": "Tenant legal entity not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        entity.delete()

        return Response(
            {
                "success": True,
                "message": "Tenant legal entity deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantTaxRegistration
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantTaxRegistrationListCreateAPIView(APIView):
    """
    GET  : Get all tenant tax registrations
    POST : Create a new tenant tax registration
    """

    permission_classes = [AllowAny]

    def get(self, request):
        registrations = TenantTaxRegistration.objects.all().order_by("-created_at")
        serializer = TenantTaxRegistrationSerializer(registrations, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant tax registrations fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantTaxRegistrationSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantTaxRegistrationSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant tax registration created successfully.",
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
class TenantTaxRegistrationRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Get tenant tax registration by pk
    PUT    : Update tenant tax registration (partial)
    DELETE : Delete tenant tax registration
    """

    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantTaxRegistration.objects.get(pk=pk)
        except TenantTaxRegistration.DoesNotExist:
            return None

    def get(self, request, pk):
        registration = self.get_object(pk)

        if not registration:
            return Response(
                {
                    "success": False,
                    "message": "Tenant tax registration not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantTaxRegistrationSerializer(registration)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=TenantTaxRegistrationSerializer)
    def put(self, request, pk):
        registration = self.get_object(pk)

        if not registration:
            return Response(
                {
                    "success": False,
                    "message": "Tenant tax registration not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantTaxRegistrationSerializer(registration, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant tax registration updated successfully.",
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
        registration = self.get_object(pk)

        if not registration:
            return Response(
                {
                    "success": False,
                    "message": "Tenant tax registration not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        registration.delete()

        return Response(
            {
                "success": True,
                "message": "Tenant tax registration deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantDomain
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantDomainListCreateAPIView(APIView):
    """
    GET  : Get all tenant domains
    POST : Create a new tenant domain
    """

    permission_classes = [AllowAny]

    def get(self, request):
        domains = TenantDomain.objects.all().order_by("-created_at")
        serializer = TenantDomainSerializer(domains, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant domains fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantDomainSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantDomainSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant domain created successfully.",
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
class TenantDomainRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Get tenant domain by pk
    PUT    : Update tenant domain (partial)
    DELETE : Delete tenant domain
    """

    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantDomain.objects.get(pk=pk)
        except TenantDomain.DoesNotExist:
            return None

    def get(self, request, pk):
        domain = self.get_object(pk)

        if not domain:
            return Response(
                {
                    "success": False,
                    "message": "Tenant domain not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantDomainSerializer(domain)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=TenantDomainSerializer)
    def put(self, request, pk):
        domain = self.get_object(pk)

        if not domain:
            return Response(
                {
                    "success": False,
                    "message": "Tenant domain not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantDomainSerializer(domain, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant domain updated successfully.",
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
        domain = self.get_object(pk)

        if not domain:
            return Response(
                {
                    "success": False,
                    "message": "Tenant domain not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        domain.delete()

        return Response(
            {
                "success": True,
                "message": "Tenant domain deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantLocation
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantLocationListCreateAPIView(APIView):
    """
    GET  : Get all tenant locations
    POST : Create a new tenant location
    """

    permission_classes = [AllowAny]

    def get(self, request):
        locations = TenantLocation.objects.all().order_by("-created_at")
        serializer = TenantLocationSerializer(locations, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant locations fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantLocationSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantLocationSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant location created successfully.",
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
class TenantLocationRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Get tenant location by pk
    PUT    : Update tenant location (partial)
    DELETE : Delete tenant location
    """

    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantLocation.objects.get(pk=pk)
        except TenantLocation.DoesNotExist:
            return None

    def get(self, request, pk):
        location = self.get_object(pk)

        if not location:
            return Response(
                {
                    "success": False,
                    "message": "Tenant location not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantLocationSerializer(location)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=TenantLocationSerializer)
    def put(self, request, pk):
        location = self.get_object(pk)

        if not location:
            return Response(
                {
                    "success": False,
                    "message": "Tenant location not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantLocationSerializer(location, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant location updated successfully.",
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
        location = self.get_object(pk)

        if not location:
            return Response(
                {
                    "success": False,
                    "message": "Tenant location not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        location.delete()

        return Response(
            {
                "success": True,
                "message": "Tenant location deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantAuthorisedRepresentative
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantAuthorisedRepresentativeListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        reps = TenantAuthorisedRepresentative.objects.all().order_by("-created_at")
        serializer = TenantAuthorisedRepresentativeSerializer(reps, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant authorised representatives fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantAuthorisedRepresentativeSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantAuthorisedRepresentativeSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant authorised representative created successfully.",
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
class TenantAuthorisedRepresentativeRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantAuthorisedRepresentative.objects.get(pk=pk)
        except TenantAuthorisedRepresentative.DoesNotExist:
            return None

    def get(self, request, pk):
        rep = self.get_object(pk)

        if not rep:
            return Response(
                {"success": False, "message": "Tenant authorised representative not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantAuthorisedRepresentativeSerializer(rep)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantAuthorisedRepresentativeSerializer)
    def put(self, request, pk):
        rep = self.get_object(pk)

        if not rep:
            return Response(
                {"success": False, "message": "Tenant authorised representative not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantAuthorisedRepresentativeSerializer(rep, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant authorised representative updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        rep = self.get_object(pk)

        if not rep:
            return Response(
                {"success": False, "message": "Tenant authorised representative not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        rep.delete()

        return Response(
            {"success": True, "message": "Tenant authorised representative deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantContact
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantContactListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        contacts = TenantContact.objects.all().order_by("-created_at")
        serializer = TenantContactSerializer(contacts, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant contacts fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantContactSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantContactSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant contact created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantContactRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantContact.objects.get(pk=pk)
        except TenantContact.DoesNotExist:
            return None

    def get(self, request, pk):
        contact = self.get_object(pk)

        if not contact:
            return Response(
                {"success": False, "message": "Tenant contact not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantContactSerializer(contact)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantContactSerializer)
    def put(self, request, pk):
        contact = self.get_object(pk)

        if not contact:
            return Response(
                {"success": False, "message": "Tenant contact not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantContactSerializer(contact, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant contact updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        contact = self.get_object(pk)

        if not contact:
            return Response(
                {"success": False, "message": "Tenant contact not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        contact.delete()

        return Response(
            {"success": True, "message": "Tenant contact deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantVerification — append-only: GET (list/retrieve) + POST only.
# No pk (no UUIDModel) -> keyed by pk. No PUT/DELETE by design.
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantVerificationListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        verifications = TenantVerification.objects.all().order_by("-created_at")
        serializer = TenantVerificationSerializer(verifications, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant verifications fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantVerificationSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantVerificationSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant verification recorded successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantVerificationRetrieveUpdateDeleteAPIView(APIView):
    """
    WARNING: PUT/DELETE here override the model's own "append-only,
    never update in place" design (see model docstring). Included only
    because full CRUD was requested — recommend removing put()/delete()
    and treating corrections as new POSTs instead.
    """

    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantVerification.objects.get(pk=pk)
        except TenantVerification.DoesNotExist:
            return None

    def get(self, request, pk):
        verification = self.get_object(pk)

        if not verification:
            return Response(
                {"success": False, "message": "Tenant verification not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantVerificationSerializer(verification)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantVerificationSerializer)
    def put(self, request, pk):
        verification = self.get_object(pk)

        if not verification:
            return Response(
                {"success": False, "message": "Tenant verification not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantVerificationSerializer(verification, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant verification updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        verification = self.get_object(pk)

        if not verification:
            return Response(
                {"success": False, "message": "Tenant verification not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        verification.delete()

        return Response(
            {"success": True, "message": "Tenant verification deleted successfully."},
            status=status.HTTP_200_OK,
        )


def _check_tenant_application_complete(tenant):
    """Shared by TenantSubmitAPIView and TenantResubmitAPIView. Queries
    each related table directly by tenant= rather than trusting a
    reverse-accessor name, since TenantOwnedModel's default related_name
    pattern varies per model and guessing it wrong fails silently.
    """
    missing = []

    if not (tenant.name and tenant.legal_name and tenant.organisation_type
            and tenant.industry_ids and tenant.default_timezone and tenant.default_currency):
        missing.append("tenant_core_details")
    if not TenantLegalEntity.objects.filter(tenant=tenant).exists():
        missing.append("legal_entity")
    if not TenantLocation.objects.filter(tenant=tenant, location_type=TenantLocation.LocationType.REGISTERED).exists():
        missing.append("registered_address")
    if not TenantAuthorisedRepresentative.objects.filter(tenant=tenant).exists():
        missing.append("authorised_representative")
    if not TenantDocument.objects.filter(tenant=tenant).exists():
        missing.append("documents")
    if not TenantLegalAcceptance.objects.filter(tenant=tenant, acceptance_type=TenantLegalAcceptance.AcceptanceType.TERMS).exists():
        missing.append("terms_acceptance")
    if not TenantOperation.objects.filter(tenant=tenant).exists():
        missing.append("operating_permission")

    return {"ok": not missing, "missing": missing}


@method_decorator(csrf_exempt, name='dispatch')
class TenantSubmitAPIView(APIView):
    """
    POST : First-time submission of a tenant's Stage 1 application.

    Checks every required related table is present (see
    _check_tenant_application_complete). If incomplete, returns which
    sections are missing. If complete, creates ONE new TenantVerification
    row (status=SUBMITTED, submitted_at=now()) for this tenant.

    Allowed only when this tenant has no TenantVerification row yet.
    Once one exists, all further activity goes through
    TenantResubmitAPIView (after RETURNED) or the review-decision
    endpoint — never a second call here.
    """

    permission_classes = [AllowAny]
    serializer_class = TenantSubmitSerializer

    @extend_schema(request=TenantSubmitSerializer)
    def post(self, request, tenant_id):
        try:
            tenant = Tenant.objects.get(pk=tenant_id)
        except Tenant.DoesNotExist:
            return Response(
                {"success": False, "message": "Tenant not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if TenantVerification.objects.filter(tenant=tenant).exists():
            return Response(
                {"success": False, "message": "This tenant has already been submitted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        completeness = _check_tenant_application_complete(tenant)
        if not completeness["ok"]:
            return Response(
                {
                    "success": False,
                    "message": "Tenant application incomplete.",
                    "missing_sections": completeness["missing"],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        verification = TenantVerification.objects.create(
            tenant=tenant,
            status=TenantVerification.Status.SUBMITTED,
            submitted_at=timezone.now(),
        )

        return Response(
            {
                "success": True,
                "message": "Tenant application submitted for review.",
                "data": {
                    "verification_id": verification.id,
                    "status": verification.status,
                    "submitted_at": verification.submitted_at,
                },
            },
            status=status.HTTP_200_OK,
        )


class TenantStage1DetailsAPIView(APIView):
    """
    GET : Everything submitted for a tenant's Stage 1 application, in
    one call — the Tenant row itself plus every related Stage 1 table
    (legal entities, tax registrations, locations, authorised
    representatives, documents, legal acceptances, operations) and a
    compact summary of the founding admin. Read-only; returns full
    table contents, not just status fields (that's
    TenantVerification-based status endpoints, not this one). Mirrors
    accounts.Stage1DetailsAPIView's shape for the professional side.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, tenant_id):
        try:
            tenant = Tenant.objects.select_related("created_by").get(pk=tenant_id)
        except Tenant.DoesNotExist:
            return Response(
                {"success": False, "message": "Tenant not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = Stage1TenantDetailsSerializer(tenant)

        return Response(
            {
                "success": True,
                "message": "Stage 1 tenant details fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name='dispatch')
class TenantResubmitAPIView(APIView):
    """
    POST : Resubmit a tenant's application after a RETURNED decision.

    Allowed only when the tenant's latest TenantVerification.status is
    RETURNED — REJECTED is terminal (no resubmit), and there's nothing
    to resubmit before a first SUBMITTED ever happens (use
    TenantSubmitAPIView for that). Re-runs the same completeness check
    as submit, then creates a NEW TenantVerification row (status=
    SUBMITTED, submitted_at=now()) — the RETURNED row is left untouched
    as history, never edited.
    """

    permission_classes = [AllowAny]
    serializer_class = TenantResubmitSerializer

    @extend_schema(request=TenantResubmitSerializer)
    def post(self, request, tenant_id):
        try:
            tenant = Tenant.objects.get(pk=tenant_id)
        except Tenant.DoesNotExist:
            return Response(
                {"success": False, "message": "Tenant not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        latest_verification = TenantVerification.objects.filter(tenant=tenant).order_by("-created_at").first()
        if latest_verification is None or latest_verification.status != TenantVerification.Status.RETURNED:
            current_status = latest_verification.status if latest_verification else "NONE"
            return Response(
                {
                    "success": False,
                    "message": f"Cannot resubmit from status={current_status}.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        completeness = _check_tenant_application_complete(tenant)
        if not completeness["ok"]:
            return Response(
                {
                    "success": False,
                    "message": "Tenant application still incomplete.",
                    "missing_sections": completeness["missing"],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        verification = TenantVerification.objects.create(
            tenant=tenant,
            status=TenantVerification.Status.SUBMITTED,
            submitted_at=timezone.now(),
        )

        return Response(
            {
                "success": True,
                "message": "Tenant application resubmitted for review.",
                "data": {
                    "verification_id": verification.id,
                    "status": verification.status,
                    "submitted_at": verification.submitted_at,
                },
            },
            status=status.HTTP_200_OK,
        )


def _create_stage3_records(tenant, reviewer, founding_admin):
    """Stage 3 — System initialization.

    Called inside the same transaction as Stage 2's approve decision.
    Creates default-records for:
      1. TenantSettings        (platform defaults)
      2. TenantSecuritySettings (platform defaults)
      3. TenantBranding         (empty)
      4. TenantLegalSettings    (defaults)
      5. TenantBilling          (empty)
      6. TenantContact ORG_ADMIN (copied from the founding applicant)
      7. TenantRoleAssignment   user=founding admin, role=ORG_ADMIN, granted_by=reviewer
    """
    created = {}

    created["tenant_settings"], _ = TenantSettings.objects.get_or_create(
        tenant=tenant,
        defaults={
            "default_language": "en",
            "date_format": "DD-MM-YYYY",
            "number_format": "1,234.56",
            "measurement_system": "METRIC",
            "working_calendar": "",
        },
    )

    created["tenant_security_settings"], _ = TenantSecuritySettings.objects.get_or_create(
        tenant=tenant,
        defaults={
            "mfa_policy": TenantSecuritySettings.MfaPolicy.OPTIONAL,
            "sso_status": TenantSecuritySettings.SsoStatus.DISABLED,
            "identity_provider": "",
            "session_policy": {},
            "api_access_status": TenantSecuritySettings.ApiAccessStatus.DISABLED,
            "export_policy": {},
        },
    )

    created["tenant_branding"], _ = TenantBranding.objects.get_or_create(
        tenant=tenant,
        defaults={
            "colours": {},
            "report_header": "",
            "report_footer": "",
            "disclaimer_text": "",
        },
    )

    created["tenant_legal_settings"], _ = TenantLegalSettings.objects.get_or_create(
        tenant=tenant,
        defaults={
            "nda_requirement": TenantLegalSettings.NdaRequirement.NOT_REQUIRED,
            "default_classification": TenantLegalSettings.Classification.INTERNAL,
            "retention_policy": "",
            "is_legal_hold": False,
        },
    )

    created["tenant_billing"], _ = TenantBilling.objects.get_or_create(
        tenant=tenant,
        defaults={
            "po_required": False,
            "po_format": "",
            "po_contact": "",
            "payment_terms": "",
        },
    )

    if founding_admin is not None:
        existing_org_admin_contact = TenantContact.objects.filter(
            tenant=tenant,
            contact_type=TenantContact.ContactType.ORG_ADMIN,
        ).first()
        if existing_org_admin_contact is None:
            full_name = ""
            email = getattr(founding_admin, "email", "") or ""
            phone = ""
            mobile_cc = getattr(founding_admin, "mobile_country_code", "") or ""
            mobile_no = getattr(founding_admin, "mobile_number", "") or ""
            if mobile_cc and mobile_no:
                phone = f"{mobile_cc}{mobile_no}"
            try:
                rep = TenantAuthorisedRepresentative.objects.filter(tenant=tenant).first()
                if rep:
                    full_name = rep.full_name or full_name
                    if rep.official_email:
                        email = rep.official_email
                    if rep.mobile:
                        phone = rep.mobile
            except Exception:
                pass
            created["tenant_contact_org_admin"] = TenantContact.objects.create(
                tenant=tenant,
                contact_type=TenantContact.ContactType.ORG_ADMIN,
                user=founding_admin,
                full_name=full_name,
                email=email,
                phone=phone,
                is_active=True,
            )
        else:
            created["tenant_contact_org_admin"] = existing_org_admin_contact

        org_admin_role = None
        try:
            org_admin_role = roles.objects.filter(
                code__iexact="ORG_ADMIN",
            ).first()
            if org_admin_role is None:
                org_admin_role = roles.objects.filter(
                    name__icontains="ORG_ADMIN",
                ).first()
            if org_admin_role is None:
                org_admin_role = roles.objects.filter(
                    roles_for__iexact="tenant admin",
                ).first()
            if org_admin_role is None:
                org_admin_role = roles.objects.filter(
                    tenant=tenant,
                ).order_by("created").first()
        except Exception:
            org_admin_role = None

        if org_admin_role is not None:
            existing_assignment = TenantRoleAssignment.objects.filter(
                user=founding_admin,
                role=org_admin_role,
                status="ACTIVE",
            ).first()
            if existing_assignment is None:
                created["tenant_role_assignment"] = TenantRoleAssignment.objects.create(
                    user=founding_admin,
                    role=org_admin_role,
                    granted_by=reviewer,
                    status="ACTIVE",
                )
            else:
                created["tenant_role_assignment"] = existing_assignment
        else:
            created["tenant_role_assignment"] = None

    return created


# @method_decorator(csrf_exempt, name='dispatch')
# class TenantReviewDecisionAPIView(APIView):
#     """
#     POST : Superadmin review decision for a tenant application.

#     Only accessible to a Platform Super Admin (UserTbl.is_superuser=True
#     and tenant=None — the platform-level account).

#     Workflow:
#       1. Validates the caller is a superadmin from UserTbl.
#       2. Loads the tenant and its LATEST TenantVerification row.
#       3. Updates that LATEST TenantVerification row in-place (NOT a new row)
#          with status, reviewed_by, reviewed_at, reason, risk_classification,
#          next_review_date.
#       4. If status == APPROVED:
#            - Tenant.status -> ACTIVE
#            - Founding legal entity -> ACTIVE + reviewed stamps
#            - Founding UserTbl approval_status -> APPROVED, is_active set
#              (only once email+mobile verified; else stays False)
#            - Stage 3 records created (TenantSettings, TenantSecuritySettings,
#              TenantBranding, TenantLegalSettings, TenantBilling,
#              TenantContact ORG_ADMIN, TenantRoleAssignment ORG_ADMIN)
#          If status == REJECTED or RETURNED:
#            - Only the latest TenantVerification is updated; no Stage 3 runs.

#     Expected request body (JSON):
#       {
#         "status": "APPROVED" | "REJECTED" | "RETURNED",
#         "reason": "required for REJECTED / RETURNED",
#         "risk_classification": "LOW" | "STANDARD" | "ENHANCED_REVIEW" | "RESTRICTED",
#         "next_review_date": "YYYY-MM-DD"
#       }
#     """

#     permission_classes = [AllowAny]
#     parser_classes = [MultiPartParser, FormParser, JSONParser]
#     serializer_class = TenantReviewDecisionSerializer

#     @extend_schema(request=TenantReviewDecisionSerializer)
#     @transaction.atomic
#     def post(self, request, tenant_id):
#         reviewer = getattr(request, "user", None)
#         if reviewer is None or not getattr(reviewer, "is_authenticated", False):
#             from rest_framework.authtoken.models import Token
#             auth_header = request.META.get("HTTP_AUTHORIZATION", "")
#             token_key = None
#             if auth_header.startswith("Token "):
#                 token_key = auth_header.split("Token ", 1)[1].strip()
#             elif auth_header.startswith("Bearer "):
#                 token_key = auth_header.split("Bearer ", 1)[1].strip()
#             if token_key:
#                 try:
#                     token = Token.objects.select_related("user").get(key=token_key)
#                     reviewer = token.user
#                 except Exception:
#                     reviewer = None

#         if reviewer is None:
#             return Response(
#                 {"success": False, "message": "Authentication required."},
#                 status=status.HTTP_401_UNAUTHORIZED,
#             )

#         if not getattr(reviewer, "is_superuser", False):
#             return Response(
#                 {
#                     "success": False,
#                     "message": "Only Platform Super Admin can review tenants.",
#                 },
#                 status=status.HTTP_403_FORBIDDEN,
#             )
#         if getattr(reviewer, "tenant_id", None) is not None:
#             return Response(
#                 {
#                     "success": False,
#                     "message": "Reviewer must be a platform-level (tenant=null) superadmin.",
#                 },
#                 status=status.HTTP_403_FORBIDDEN,
#             )

#         try:
#             tenant = Tenant.objects.select_related("created_by").get(pk=tenant_id)
#         except Tenant.DoesNotExist:
#             return Response(
#                 {"success": False, "message": "Tenant not found."},
#                 status=status.HTTP_404_NOT_FOUND,
#             )

#         latest_verification = (
#             TenantVerification.objects.filter(tenant=tenant)
#             .order_by("-created_at")
#             .first()
#         )
#         if latest_verification is None:
#             return Response(
#                 {
#                     "success": False,
#                     "message": "No TenantVerification record found for this tenant — submit first.",
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         if latest_verification.status not in {
#             TenantVerification.Status.SUBMITTED,
#             TenantVerification.Status.UNDER_REVIEW,
#             TenantVerification.Status.RETURNED,
#         }:
#             return Response(
#                 {
#                     "success": False,
#                     "message": f"Cannot review from status={latest_verification.status}.",
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         if latest_verification.reviewed_by_id is not None:
#             return Response(
#                 {
#                     "success": False,
#                     "message": "This verification record has already been reviewed.",
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         serializer = TenantReviewDecisionSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(
#                 {"success": False, "errors": serializer.errors},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         decision = serializer.validated_data
#         new_status = decision["status"]
#         now = timezone.now()

#         latest_verification.status = new_status
#         latest_verification.reviewed_by = reviewer
#         latest_verification.reviewed_at = now
#         latest_verification.reason = decision.get("reason", "") or ""
#         latest_verification.risk_classification = decision.get("risk_classification", "STANDARD")
#         latest_verification.next_review_date = decision.get("next_review_date")
#         latest_verification.save()

#         stage3 = None
#         founding_admin = tenant.created_by

#         if new_status == "APPROVED":
#             tenant.status = Tenant.Status.ACTIVE
#             if tenant.status_reason is None or tenant.status_reason == "":
#                 tenant.status_reason = "Approved via tenant review"
#             tenant.save()

#             founding_entity = TenantLegalEntity.objects.filter(tenant=tenant).order_by("created_at").first()
#             if founding_entity is not None and founding_entity.status != TenantLegalEntity.Status.ACTIVE:
#                 founding_entity.status = TenantLegalEntity.Status.ACTIVE
#                 founding_entity.reviewed_by = reviewer
#                 founding_entity.reviewed_at = now
#                 founding_entity.save()

#             if founding_admin is not None:
#                 founding_admin.approval_status = UserTbl.ApprovalStatus.APPROVED
#                 founding_admin.approved_by = reviewer
#                 founding_admin.approved_at = now
#                 email_ok = founding_admin.email_verified_at is not None
#                 mobile_ok = founding_admin.mobile_verified_at is not None
#                 if email_ok and mobile_ok:
#                     founding_admin.is_active = True
#                 founding_admin.save()

#             stage3 = _create_stage3_records(tenant, reviewer, founding_admin)

#             for op in TenantOperation.objects.filter(tenant=tenant):
#                 if op.status == TenantOperation.Status.PENDING:
#                     op.status = TenantOperation.Status.ACTIVE
#                     op.reviewed_by = reviewer
#                     op.reviewed_at = now
#                     op.save()

#         response_data = {
#             "verification_id": latest_verification.id,
#             "tenant_id": tenant.id,
#             "status": latest_verification.status,
#             "reviewed_by": str(getattr(reviewer, "public_id", reviewer.id)),
#             "reviewed_at": latest_verification.reviewed_at.isoformat() if latest_verification.reviewed_at else None,
#             "reason": latest_verification.reason,
#             "risk_classification": latest_verification.risk_classification,
#             "next_review_date": str(latest_verification.next_review_date) if latest_verification.next_review_date else None,
#         }
#         if stage3 is not None:
#             response_data["stage3_created"] = {k: (str(v.id) if v is not None else None) for k, v in stage3.items()}

#         return Response(
#             {
#                 "success": True,
#                 "message": f"Tenant review decision recorded: {new_status}.",
#                 "data": response_data,
#             },
#             status=status.HTTP_200_OK,
#         )

@method_decorator(csrf_exempt, name='dispatch')
class TenantReviewDecisionAPIView(APIView):
    """
    POST : Review decision for a tenant application.

    NOTE: This endpoint is now open (no authentication/authorization
    required). Anyone can call it. `reviewer` will be the request's
    attached user if one happens to be present (e.g. via some other
    upstream middleware), otherwise it is None, and reviewed_by /
    granted_by on the created records will be null.

    Workflow:
      1. Loads the tenant and its LATEST TenantVerification row.
      2. Updates that LATEST TenantVerification row in-place (NOT a new row)
         with status, reviewed_by, reviewed_at, reason, risk_classification,
         next_review_date.
      3. If status == APPROVED:
           - Tenant.status -> ACTIVE
           - Founding legal entity -> ACTIVE + reviewed stamps
           - Founding UserTbl approval_status -> APPROVED, is_active set
             (only once email+mobile verified; else stays False)
           - Stage 3 records created (TenantSettings, TenantSecuritySettings,
             TenantBranding, TenantLegalSettings, TenantBilling,
             TenantContact ORG_ADMIN, TenantRoleAssignment ORG_ADMIN)
         If status == REJECTED or RETURNED:
           - Only the latest TenantVerification is updated; no Stage 3 runs.

    Expected request body (JSON):
      {
        "status": "APPROVED" | "REJECTED" | "RETURNED",
        "reason": "required for REJECTED / RETURNED",
        "risk_classification": "LOW" | "STANDARD" | "ENHANCED_REVIEW" | "RESTRICTED",
        "next_review_date": "YYYY-MM-DD"
      }
    """

    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = TenantReviewDecisionSerializer

    @extend_schema(request=TenantReviewDecisionSerializer)
    @transaction.atomic
    def post(self, request, tenant_id):
        # Open API: no authentication required. Use request.user if present,
        # otherwise reviewer stays None.
        reviewer = getattr(request, "user", None)
        if reviewer is not None and not getattr(reviewer, "is_authenticated", False):
            reviewer = None

        try:
            tenant = Tenant.objects.select_related("created_by").get(pk=tenant_id)
        except Tenant.DoesNotExist:
            return Response(
                {"success": False, "message": "Tenant not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        latest_verification = (
            TenantVerification.objects.filter(tenant=tenant)
            .order_by("-created_at")
            .first()
        )
        if latest_verification is None:
            return Response(
                {
                    "success": False,
                    "message": "No TenantVerification record found for this tenant — submit first.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if latest_verification.status not in {
            TenantVerification.Status.SUBMITTED,
            TenantVerification.Status.UNDER_REVIEW,
            TenantVerification.Status.RETURNED,
        }:
            return Response(
                {
                    "success": False,
                    "message": f"Cannot review from status={latest_verification.status}.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if latest_verification.reviewed_by_id is not None:
            return Response(
                {
                    "success": False,
                    "message": "This verification record has already been reviewed.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TenantReviewDecisionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        decision = serializer.validated_data
        new_status = decision["status"]
        now = timezone.now()

        latest_verification.status = new_status
        latest_verification.reviewed_by = reviewer
        latest_verification.reviewed_at = now
        latest_verification.reason = decision.get("reason", "") or ""
        latest_verification.risk_classification = decision.get("risk_classification", "STANDARD")
        latest_verification.next_review_date = decision.get("next_review_date")
        latest_verification.save()

        stage3 = None
        founding_admin = tenant.created_by

        if new_status == "APPROVED":
            tenant.status = Tenant.Status.ACTIVE
            if tenant.status_reason is None or tenant.status_reason == "":
                tenant.status_reason = "Approved via tenant review"
            tenant.save()

            founding_entity = TenantLegalEntity.objects.filter(tenant=tenant).order_by("created_at").first()
            if founding_entity is not None and founding_entity.status != TenantLegalEntity.Status.ACTIVE:
                founding_entity.status = TenantLegalEntity.Status.ACTIVE
                founding_entity.reviewed_by = reviewer
                founding_entity.reviewed_at = now
                founding_entity.save()

            if founding_admin is not None:
                founding_admin.approval_status = UserTbl.ApprovalStatus.APPROVED
                founding_admin.approved_by = reviewer
                founding_admin.approved_at = now
                email_ok = founding_admin.email_verified_at is not None
                mobile_ok = founding_admin.mobile_verified_at is not None
                if email_ok and mobile_ok:
                    founding_admin.is_active = True
                founding_admin.save()

            stage3 = _create_stage3_records(tenant, reviewer, founding_admin)

            for op in TenantOperation.objects.filter(tenant=tenant):
                if op.status == TenantOperation.Status.PENDING:
                    op.status = TenantOperation.Status.ACTIVE
                    op.reviewed_by = reviewer
                    op.reviewed_at = now
                    op.save()

        response_data = {
            "verification_id": latest_verification.id,
            "tenant_id": tenant.id,
            "status": latest_verification.status,
            "reviewed_by": (
                str(getattr(reviewer, "public_id", reviewer.id)) if reviewer is not None else None
            ),
            "reviewed_at": latest_verification.reviewed_at.isoformat() if latest_verification.reviewed_at else None,
            "reason": latest_verification.reason,
            "risk_classification": latest_verification.risk_classification,
            "next_review_date": str(latest_verification.next_review_date) if latest_verification.next_review_date else None,
        }
        if stage3 is not None:
            response_data["stage3_created"] = {k: (str(v.id) if v is not None else None) for k, v in stage3.items()}

        return Response(
            {
                "success": True,
                "message": f"Tenant review decision recorded: {new_status}.",
                "data": response_data,
            },
            status=status.HTTP_200_OK,
        )
# ---------------------------------------------------------------------
# TenantDocument — file upload, multipart
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantDocumentListCreateAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        documents = TenantDocument.objects.all().order_by("-created_at")
        serializer = TenantDocumentSerializer(documents, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant documents fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantDocumentSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantDocumentSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant document created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantDocumentRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return TenantDocument.objects.get(pk=pk)
        except TenantDocument.DoesNotExist:
            return None

    def get(self, request, pk):
        document = self.get_object(pk)

        if not document:
            return Response(
                {"success": False, "message": "Tenant document not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantDocumentSerializer(document)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantDocumentSerializer)
    def put(self, request, pk):
        document = self.get_object(pk)

        if not document:
            return Response(
                {"success": False, "message": "Tenant document not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantDocumentSerializer(document, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant document updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        document = self.get_object(pk)

        if not document:
            return Response(
                {"success": False, "message": "Tenant document not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        document.delete()

        return Response(
            {"success": True, "message": "Tenant document deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantLegalAcceptance — audit-trail nature: GET + POST only.
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantLegalAcceptanceListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        acceptances = TenantLegalAcceptance.objects.all().order_by("-created_at")
        serializer = TenantLegalAcceptanceSerializer(acceptances, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant legal acceptances fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantLegalAcceptanceSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantLegalAcceptanceSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant legal acceptance recorded successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantLegalAcceptanceRetrieveAPIView(APIView):
    """GET only — acceptance records are evidence of a point-in-time action; not editable/deletable."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantLegalAcceptance.objects.get(pk=pk)
        except TenantLegalAcceptance.DoesNotExist:
            return None

    def get(self, request, pk):
        acceptance = self.get_object(pk)

        if not acceptance:
            return Response(
                {"success": False, "message": "Tenant legal acceptance not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantLegalAcceptanceSerializer(acceptance)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------
# TenantLegalSettings — singleton per tenant (OneToOneField)
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantLegalSettingsListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        settings_qs = TenantLegalSettings.objects.all().order_by("-updated_at")
        serializer = TenantLegalSettingsSerializer(settings_qs, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant legal settings fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantLegalSettingsSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantLegalSettingsSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant legal settings created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantLegalSettingsRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantLegalSettings.objects.get(pk=pk)
        except TenantLegalSettings.DoesNotExist:
            return None

    def get(self, request, pk):
        settings_obj = self.get_object(pk)

        if not settings_obj:
            return Response(
                {"success": False, "message": "Tenant legal settings not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantLegalSettingsSerializer(settings_obj)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantLegalSettingsSerializer)
    def put(self, request, pk):
        settings_obj = self.get_object(pk)

        if not settings_obj:
            return Response(
                {"success": False, "message": "Tenant legal settings not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantLegalSettingsSerializer(settings_obj, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant legal settings updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        settings_obj = self.get_object(pk)

        if not settings_obj:
            return Response(
                {"success": False, "message": "Tenant legal settings not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        settings_obj.delete()

        return Response(
            {"success": True, "message": "Tenant legal settings deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantNda
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantNdaListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        ndas = TenantNda.objects.all().order_by("-created_at")
        serializer = TenantNdaSerializer(ndas, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant NDAs fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantNdaSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantNdaSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant NDA created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantNdaRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantNda.objects.get(pk=pk)
        except TenantNda.DoesNotExist:
            return None

    def get(self, request, pk):
        nda = self.get_object(pk)

        if not nda:
            return Response(
                {"success": False, "message": "Tenant NDA not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantNdaSerializer(nda)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantNdaSerializer)
    def put(self, request, pk):
        nda = self.get_object(pk)

        if not nda:
            return Response(
                {"success": False, "message": "Tenant NDA not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantNdaSerializer(nda, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant NDA updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        nda = self.get_object(pk)

        if not nda:
            return Response(
                {"success": False, "message": "Tenant NDA not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        nda.delete()

        return Response(
            {"success": True, "message": "Tenant NDA deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantSettings — singleton per tenant (OneToOneField)
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantSettingsListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        settings_qs = TenantSettings.objects.all().order_by("-updated_at")
        serializer = TenantSettingsSerializer(settings_qs, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant settings fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantSettingsSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantSettingsSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant settings created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantSettingsRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantSettings.objects.get(pk=pk)
        except TenantSettings.DoesNotExist:
            return None

    def get(self, request, pk):
        settings_obj = self.get_object(pk)

        if not settings_obj:
            return Response(
                {"success": False, "message": "Tenant settings not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantSettingsSerializer(settings_obj)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantSettingsSerializer)
    def put(self, request, pk):
        settings_obj = self.get_object(pk)

        if not settings_obj:
            return Response(
                {"success": False, "message": "Tenant settings not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantSettingsSerializer(settings_obj, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant settings updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        settings_obj = self.get_object(pk)

        if not settings_obj:
            return Response(
                {"success": False, "message": "Tenant settings not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        settings_obj.delete()

        return Response(
            {"success": True, "message": "Tenant settings deleted successfully."},
            status=status.HTTP_200_OK,
        )

# ---------------------------------------------------------------------
# TenantSubscription — versioned: GET + POST only, no edit-in-place.
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantSubscriptionListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        subscriptions = TenantSubscription.objects.all().order_by("-created_at")
        serializer = TenantSubscriptionSerializer(subscriptions, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant subscriptions fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantSubscriptionSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantSubscriptionSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant subscription recorded successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantSubscriptionRetrieveAPIView(APIView):
    """GET only — plan changes are versioned as new rows, never edited in place (see model docstring)."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantSubscription.objects.get(pk=pk)
        except TenantSubscription.DoesNotExist:
            return None

    def get(self, request, pk):
        subscription = self.get_object(pk)

        if not subscription:
            return Response(
                {"success": False, "message": "Tenant subscription not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantSubscriptionSerializer(subscription)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------
# Module — platform-level master data, no tenant.
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class ModuleListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        modules = Module.objects.all().order_by("code")
        serializer = ModuleSerializer(modules, many=True)

        return Response(
            {
                "success": True,
                "message": "Modules fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(ModuleSerializer))
    def post(self, request):
        serializer = _create_serializer(ModuleSerializer, request)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Module created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class ModuleRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return Module.objects.get(pk=pk)
        except Module.DoesNotExist:
            return None

    def get(self, request, pk):
        module = self.get_object(pk)

        if not module:
            return Response(
                {"success": False, "message": "Module not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ModuleSerializer(module)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=ModuleSerializer)
    def put(self, request, pk):
        module = self.get_object(pk)

        if not module:
            return Response(
                {"success": False, "message": "Module not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ModuleSerializer(module, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Module updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        module = self.get_object(pk)

        if not module:
            return Response(
                {"success": False, "message": "Module not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        module.delete()

        return Response(
            {"success": True, "message": "Module deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantModuleEntitlement
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantModuleEntitlementListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        entitlements = TenantModuleEntitlement.objects.all().order_by("-created_at")
        serializer = TenantModuleEntitlementSerializer(entitlements, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant module entitlements fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantModuleEntitlementSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantModuleEntitlementSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant module entitlement created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantModuleEntitlementRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantModuleEntitlement.objects.get(pk=pk)
        except TenantModuleEntitlement.DoesNotExist:
            return None

    def get(self, request, pk):
        entitlement = self.get_object(pk)

        if not entitlement:
            return Response(
                {"success": False, "message": "Tenant module entitlement not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantModuleEntitlementSerializer(entitlement)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantModuleEntitlementSerializer)
    def put(self, request, pk):
        entitlement = self.get_object(pk)

        if not entitlement:
            return Response(
                {"success": False, "message": "Tenant module entitlement not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantModuleEntitlementSerializer(entitlement, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant module entitlement updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        entitlement = self.get_object(pk)

        if not entitlement:
            return Response(
                {"success": False, "message": "Tenant module entitlement not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        entitlement.delete()

        return Response(
            {"success": True, "message": "Tenant module entitlement deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantBranding — singleton per tenant, image upload.
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantBrandingListCreateAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        brandings = TenantBranding.objects.all().order_by("-updated_at")
        serializer = TenantBrandingSerializer(brandings, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant brandings fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantBrandingSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantBrandingSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant branding created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantBrandingRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return TenantBranding.objects.get(pk=pk)
        except TenantBranding.DoesNotExist:
            return None

    def get(self, request, pk):
        branding = self.get_object(pk)

        if not branding:
            return Response(
                {"success": False, "message": "Tenant branding not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantBrandingSerializer(branding)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantBrandingSerializer)
    def put(self, request, pk):
        branding = self.get_object(pk)

        if not branding:
            return Response(
                {"success": False, "message": "Tenant branding not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantBrandingSerializer(branding, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant branding updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        branding = self.get_object(pk)

        if not branding:
            return Response(
                {"success": False, "message": "Tenant branding not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        branding.delete()

        return Response(
            {"success": True, "message": "Tenant branding deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantReportTemplate — file upload.
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantReportTemplateListCreateAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        templates = TenantReportTemplate.objects.all().order_by("-created_at")
        serializer = TenantReportTemplateSerializer(templates, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant report templates fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantReportTemplateSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantReportTemplateSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant report template created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantReportTemplateRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return TenantReportTemplate.objects.get(pk=pk)
        except TenantReportTemplate.DoesNotExist:
            return None

    def get(self, request, pk):
        template = self.get_object(pk)

        if not template:
            return Response(
                {"success": False, "message": "Tenant report template not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantReportTemplateSerializer(template)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantReportTemplateSerializer)
    def put(self, request, pk):
        template = self.get_object(pk)

        if not template:
            return Response(
                {"success": False, "message": "Tenant report template not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantReportTemplateSerializer(template, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant report template updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        template = self.get_object(pk)

        if not template:
            return Response(
                {"success": False, "message": "Tenant report template not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        template.delete()

        return Response(
            {"success": True, "message": "Tenant report template deleted successfully."},
            status=status.HTTP_200_OK,
        )

# ---------------------------------------------------------------------
# TenantSecuritySettings — singleton per tenant.
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantSecuritySettingsListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        settings_qs = TenantSecuritySettings.objects.all().order_by("-updated_at")
        serializer = TenantSecuritySettingsSerializer(settings_qs, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant security settings fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantSecuritySettingsSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantSecuritySettingsSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant security settings created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantSecuritySettingsRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantSecuritySettings.objects.get(pk=pk)
        except TenantSecuritySettings.DoesNotExist:
            return None

    def get(self, request, pk):
        settings_obj = self.get_object(pk)

        if not settings_obj:
            return Response(
                {"success": False, "message": "Tenant security settings not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantSecuritySettingsSerializer(settings_obj)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantSecuritySettingsSerializer)
    def put(self, request, pk):
        settings_obj = self.get_object(pk)

        if not settings_obj:
            return Response(
                {"success": False, "message": "Tenant security settings not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantSecuritySettingsSerializer(settings_obj, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant security settings updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        settings_obj = self.get_object(pk)

        if not settings_obj:
            return Response(
                {"success": False, "message": "Tenant security settings not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        settings_obj.delete()

        return Response(
            {"success": True, "message": "Tenant security settings deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantIPRestriction — nested under security_settings, no tenant FK.
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantIPRestrictionListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        restrictions = TenantIPRestriction.objects.all().order_by("-created_at")
        serializer = TenantIPRestrictionSerializer(restrictions, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant IP restrictions fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantIPRestrictionSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantIPRestrictionSerializer, request)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant IP restriction created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantIPRestrictionRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantIPRestriction.objects.get(pk=pk)
        except TenantIPRestriction.DoesNotExist:
            return None

    def get(self, request, pk):
        restriction = self.get_object(pk)

        if not restriction:
            return Response(
                {"success": False, "message": "Tenant IP restriction not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantIPRestrictionSerializer(restriction)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantIPRestrictionSerializer)
    def put(self, request, pk):
        restriction = self.get_object(pk)

        if not restriction:
            return Response(
                {"success": False, "message": "Tenant IP restriction not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantIPRestrictionSerializer(restriction, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant IP restriction updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        restriction = self.get_object(pk)

        if not restriction:
            return Response(
                {"success": False, "message": "Tenant IP restriction not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        restriction.delete()

        return Response(
            {"success": True, "message": "Tenant IP restriction deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantIntegration — secret_reference is write_only, never returned.
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantIntegrationListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        integrations = TenantIntegration.objects.all().order_by("-created_at")
        serializer = TenantIntegrationSerializer(integrations, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant integrations fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantIntegrationSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantIntegrationSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant integration created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantIntegrationRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantIntegration.objects.get(pk=pk)
        except TenantIntegration.DoesNotExist:
            return None

    def get(self, request, pk):
        integration = self.get_object(pk)

        if not integration:
            return Response(
                {"success": False, "message": "Tenant integration not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantIntegrationSerializer(integration)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantIntegrationSerializer)
    def put(self, request, pk):
        integration = self.get_object(pk)

        if not integration:
            return Response(
                {"success": False, "message": "Tenant integration not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantIntegrationSerializer(integration, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant integration updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        integration = self.get_object(pk)

        if not integration:
            return Response(
                {"success": False, "message": "Tenant integration not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        integration.delete()

        return Response(
            {"success": True, "message": "Tenant integration deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantBilling — singleton per tenant.
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantBillingListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        billings = TenantBilling.objects.all().order_by("-updated_at")
        serializer = TenantBillingSerializer(billings, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant billing records fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantBillingSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantBillingSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant billing created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantBillingRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantBilling.objects.get(pk=pk)
        except TenantBilling.DoesNotExist:
            return None

    def get(self, request, pk):
        billing = self.get_object(pk)

        if not billing:
            return Response(
                {"success": False, "message": "Tenant billing not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantBillingSerializer(billing)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantBillingSerializer)
    def put(self, request, pk):
        billing = self.get_object(pk)

        if not billing:
            return Response(
                {"success": False, "message": "Tenant billing not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantBillingSerializer(billing, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant billing updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        billing = self.get_object(pk)

        if not billing:
            return Response(
                {"success": False, "message": "Tenant billing not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        billing.delete()

        return Response(
            {"success": True, "message": "Tenant billing deleted successfully."},
            status=status.HTTP_200_OK,
        )

# ---------------------------------------------------------------------
# TenantInvitation
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantInvitationListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        invitations = TenantInvitation.objects.all().order_by("-sent_at")
        serializer = TenantInvitationSerializer(invitations, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant invitations fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantInvitationSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantInvitationSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant invitation created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantInvitationRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantInvitation.objects.get(pk=pk)
        except TenantInvitation.DoesNotExist:
            return None

    def get(self, request, pk):
        invitation = self.get_object(pk)

        if not invitation:
            return Response(
                {"success": False, "message": "Tenant invitation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantInvitationSerializer(invitation)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantInvitationSerializer)
    def put(self, request, pk):
        invitation = self.get_object(pk)

        if not invitation:
            return Response(
                {"success": False, "message": "Tenant invitation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantInvitationSerializer(invitation, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant invitation updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        invitation = self.get_object(pk)

        if not invitation:
            return Response(
                {"success": False, "message": "Tenant invitation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        invitation.delete()

        return Response(
            {"success": True, "message": "Tenant invitation deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantWorkflow
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantWorkflowListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        workflows = TenantWorkflow.objects.all().order_by("-created_at")
        serializer = TenantWorkflowSerializer(workflows, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant workflows fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantWorkflowSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantWorkflowSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant workflow created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantWorkflowRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantWorkflow.objects.get(pk=pk)
        except TenantWorkflow.DoesNotExist:
            return None

    def get(self, request, pk):
        workflow = self.get_object(pk)

        if not workflow:
            return Response(
                {"success": False, "message": "Tenant workflow not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantWorkflowSerializer(workflow)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantWorkflowSerializer)
    def put(self, request, pk):
        workflow = self.get_object(pk)

        if not workflow:
            return Response(
                {"success": False, "message": "Tenant workflow not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantWorkflowSerializer(workflow, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant workflow updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        workflow = self.get_object(pk)

        if not workflow:
            return Response(
                {"success": False, "message": "Tenant workflow not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        workflow.delete()

        return Response(
            {"success": True, "message": "Tenant workflow deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantWorkflowStep — nested under workflow, no tenant FK of its own.
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantWorkflowStepListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        steps = TenantWorkflowStep.objects.all().order_by("workflow", "step_order")
        serializer = TenantWorkflowStepSerializer(steps, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant workflow steps fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantWorkflowStepSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantWorkflowStepSerializer, request)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant workflow step created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantWorkflowStepRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantWorkflowStep.objects.get(pk=pk)
        except TenantWorkflowStep.DoesNotExist:
            return None

    def get(self, request, pk):
        step = self.get_object(pk)

        if not step:
            return Response(
                {"success": False, "message": "Tenant workflow step not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantWorkflowStepSerializer(step)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantWorkflowStepSerializer)
    def put(self, request, pk):
        step = self.get_object(pk)

        if not step:
            return Response(
                {"success": False, "message": "Tenant workflow step not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantWorkflowStepSerializer(step, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant workflow step updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        step = self.get_object(pk)

        if not step:
            return Response(
                {"success": False, "message": "Tenant workflow step not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        step.delete()

        return Response(
            {"success": True, "message": "Tenant workflow step deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantOperationLog
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantOperationLogListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        logs = TenantOperationLog.objects.all().order_by("-started_at")
        serializer = TenantOperationLogSerializer(logs, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant operation logs fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantOperationLogSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantOperationLogSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant operation log created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantOperationLogRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantOperationLog.objects.get(pk=pk)
        except TenantOperationLog.DoesNotExist:
            return None

    def get(self, request, pk):
        log = self.get_object(pk)

        if not log:
            return Response(
                {"success": False, "message": "Tenant operation log not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantOperationLogSerializer(log)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantOperationLogSerializer)
    def put(self, request, pk):
        log = self.get_object(pk)

        if not log:
            return Response(
                {"success": False, "message": "Tenant operation log not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantOperationLogSerializer(log, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant operation log updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        log = self.get_object(pk)

        if not log:
            return Response(
                {"success": False, "message": "Tenant operation log not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        log.delete()

        return Response(
            {"success": True, "message": "Tenant operation log deleted successfully."},
            status=status.HTTP_200_OK,
        )


 
# ---------------------------------------------------------------------
# TenantTerminology
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantTerminologyListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        terms = TenantTerminology.objects.all().order_by("canonical_code")
        serializer = TenantTerminologySerializer(terms, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant terminology fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantTerminologySerializer))
    def post(self, request):
        serializer = _create_serializer(TenantTerminologySerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant terminology created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantTerminologyRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantTerminology.objects.get(pk=pk)
        except TenantTerminology.DoesNotExist:
            return None

    def get(self, request, pk):
        term = self.get_object(pk)

        if not term:
            return Response(
                {"success": False, "message": "Tenant terminology not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantTerminologySerializer(term)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantTerminologySerializer)
    def put(self, request, pk):
        term = self.get_object(pk)

        if not term:
            return Response(
                {"success": False, "message": "Tenant terminology not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantTerminologySerializer(term, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant terminology updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        term = self.get_object(pk)

        if not term:
            return Response(
                {"success": False, "message": "Tenant terminology not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        term.delete()

        return Response(
            {"success": True, "message": "Tenant terminology deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantNumberingConfig
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantNumberingConfigListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        configs = TenantNumberingConfig.objects.all().order_by("document_type")
        serializer = TenantNumberingConfigSerializer(configs, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant numbering configs fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantNumberingConfigSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantNumberingConfigSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant numbering config created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantNumberingConfigRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantNumberingConfig.objects.get(pk=pk)
        except TenantNumberingConfig.DoesNotExist:
            return None

    def get(self, request, pk):
        config = self.get_object(pk)

        if not config:
            return Response(
                {"success": False, "message": "Tenant numbering config not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantNumberingConfigSerializer(config)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantNumberingConfigSerializer)
    def put(self, request, pk):
        config = self.get_object(pk)

        if not config:
            return Response(
                {"success": False, "message": "Tenant numbering config not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantNumberingConfigSerializer(config, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant numbering config updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        config = self.get_object(pk)

        if not config:
            return Response(
                {"success": False, "message": "Tenant numbering config not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        config.delete()

        return Response(
            {"success": True, "message": "Tenant numbering config deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantApprovalMatrix
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantApprovalMatrixListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        matrices = TenantApprovalMatrix.objects.all().order_by("-created_at")
        serializer = TenantApprovalMatrixSerializer(matrices, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant approval matrices fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantApprovalMatrixSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantApprovalMatrixSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant approval matrix created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantApprovalMatrixRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantApprovalMatrix.objects.get(pk=pk)
        except TenantApprovalMatrix.DoesNotExist:
            return None

    def get(self, request, pk):
        matrix = self.get_object(pk)

        if not matrix:
            return Response(
                {"success": False, "message": "Tenant approval matrix not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantApprovalMatrixSerializer(matrix)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantApprovalMatrixSerializer)
    def put(self, request, pk):
        matrix = self.get_object(pk)

        if not matrix:
            return Response(
                {"success": False, "message": "Tenant approval matrix not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantApprovalMatrixSerializer(matrix, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant approval matrix updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        matrix = self.get_object(pk)

        if not matrix:
            return Response(
                {"success": False, "message": "Tenant approval matrix not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        matrix.delete()

        return Response(
            {"success": True, "message": "Tenant approval matrix deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantNotificationSettings
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantNotificationSettingsListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        settings_qs = TenantNotificationSettings.objects.all().order_by("-created_at")
        serializer = TenantNotificationSettingsSerializer(settings_qs, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant notification settings fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(TenantNotificationSettingsSerializer))
    def post(self, request):
        serializer = _create_serializer(TenantNotificationSettingsSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant notification settings created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TenantNotificationSettingsRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return TenantNotificationSettings.objects.get(pk=pk)
        except TenantNotificationSettings.DoesNotExist:
            return None

    def get(self, request, pk):
        settings_obj = self.get_object(pk)

        if not settings_obj:
            return Response(
                {"success": False, "message": "Tenant notification settings not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantNotificationSettingsSerializer(settings_obj)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantNotificationSettingsSerializer)
    def put(self, request, pk):
        settings_obj = self.get_object(pk)

        if not settings_obj:
            return Response(
                {"success": False, "message": "Tenant notification settings not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantNotificationSettingsSerializer(settings_obj, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant notification settings updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        settings_obj = self.get_object(pk)

        if not settings_obj:
            return Response(
                {"success": False, "message": "Tenant notification settings not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        settings_obj.delete()

        return Response(
            {"success": True, "message": "Tenant notification settings deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# ConflictOfInterestDeclaration
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class ConflictOfInterestDeclarationListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        declarations = ConflictOfInterestDeclaration.objects.all().order_by("-created_at")
        serializer = ConflictOfInterestDeclarationSerializer(declarations, many=True)

        return Response(
            {
                "success": True,
                "message": "Conflict of interest declarations fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(ConflictOfInterestDeclarationSerializer))
    def post(self, request):
        serializer = _create_serializer(ConflictOfInterestDeclarationSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Conflict of interest declaration created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class ConflictOfInterestDeclarationRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return ConflictOfInterestDeclaration.objects.get(pk=pk)
        except ConflictOfInterestDeclaration.DoesNotExist:
            return None

    def get(self, request, pk):
        declaration = self.get_object(pk)

        if not declaration:
            return Response(
                {"success": False, "message": "Conflict of interest declaration not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ConflictOfInterestDeclarationSerializer(declaration)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=ConflictOfInterestDeclarationSerializer)
    def put(self, request, pk):
        declaration = self.get_object(pk)

        if not declaration:
            return Response(
                {"success": False, "message": "Conflict of interest declaration not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = ConflictOfInterestDeclarationSerializer(declaration, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Conflict of interest declaration updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        declaration = self.get_object(pk)

        if not declaration:
            return Response(
                {"success": False, "message": "Conflict of interest declaration not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        declaration.delete()

        return Response(
            {"success": True, "message": "Conflict of interest declaration deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# DataExportRequest
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class DataExportRequestListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        requests_qs = DataExportRequest.objects.all().order_by("-created_at")
        serializer = DataExportRequestSerializer(requests_qs, many=True)

        return Response(
            {
                "success": True,
                "message": "Data export requests fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(DataExportRequestSerializer))
    def post(self, request):
        serializer = _create_serializer(DataExportRequestSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Data export request created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class DataExportRequestRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return DataExportRequest.objects.get(pk=pk)
        except DataExportRequest.DoesNotExist:
            return None

    def get(self, request, pk):
        export_request = self.get_object(pk)

        if not export_request:
            return Response(
                {"success": False, "message": "Data export request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DataExportRequestSerializer(export_request)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=DataExportRequestSerializer)
    def put(self, request, pk):
        export_request = self.get_object(pk)

        if not export_request:
            return Response(
                {"success": False, "message": "Data export request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = DataExportRequestSerializer(export_request, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Data export request updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        export_request = self.get_object(pk)

        if not export_request:
            return Response(
                {"success": False, "message": "Data export request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        export_request.delete()

        return Response(
            {"success": True, "message": "Data export request deleted successfully."},
            status=status.HTTP_200_OK,
        )



# ---------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class ProjectListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        projects = Project.objects.all().order_by("-created_at")
        serializer = ProjectSerializer(projects, many=True)

        return Response(
            {
                "success": True,
                "message": "Projects fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(ProjectSerializer))
    def post(self, request):
        serializer = _create_serializer(ProjectSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Project created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class ProjectRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return None

    def get(self, request, pk):
        project = self.get_object(pk)

        if not project:
            return Response(
                {"success": False, "message": "Project not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectSerializer(project)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=ProjectSerializer)
    def put(self, request, pk):
        project = self.get_object(pk)

        if not project:
            return Response(
                {"success": False, "message": "Project not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = ProjectSerializer(project, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Project updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        project = self.get_object(pk)

        if not project:
            return Response(
                {"success": False, "message": "Project not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        project.delete()

        return Response(
            {"success": True, "message": "Project deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# ProjectRequirement — no tenant field of its own (reached via project).
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class ProjectRequirementListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        requirements = ProjectRequirement.objects.all().order_by("-id")
        serializer = ProjectRequirementSerializer(requirements, many=True)

        return Response(
            {
                "success": True,
                "message": "Project requirements fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(ProjectRequirementSerializer))
    def post(self, request):
        serializer = _create_serializer(ProjectRequirementSerializer, request)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Project requirement created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class ProjectRequirementRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return ProjectRequirement.objects.get(pk=pk)
        except ProjectRequirement.DoesNotExist:
            return None

    def get(self, request, pk):
        requirement = self.get_object(pk)

        if not requirement:
            return Response(
                {"success": False, "message": "Project requirement not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectRequirementSerializer(requirement)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=ProjectRequirementSerializer)
    def put(self, request, pk):
        requirement = self.get_object(pk)

        if not requirement:
            return Response(
                {"success": False, "message": "Project requirement not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectRequirementSerializer(requirement, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Project requirement updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        requirement = self.get_object(pk)

        if not requirement:
            return Response(
                {"success": False, "message": "Project requirement not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        requirement.delete()

        return Response(
            {"success": True, "message": "Project requirement deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# ProjectRequirementScope
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class ProjectRequirementScopeListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        scopes = ProjectRequirementScope.objects.all().order_by("-id")
        serializer = ProjectRequirementScopeSerializer(scopes, many=True)

        return Response(
            {
                "success": True,
                "message": "Project requirement scopes fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(ProjectRequirementScopeSerializer))
    def post(self, request):
        serializer = _create_serializer(ProjectRequirementScopeSerializer, request)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Project requirement scope created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class ProjectRequirementScopeRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return ProjectRequirementScope.objects.get(pk=pk)
        except ProjectRequirementScope.DoesNotExist:
            return None

    def get(self, request, pk):
        scope = self.get_object(pk)

        if not scope:
            return Response(
                {"success": False, "message": "Project requirement scope not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectRequirementScopeSerializer(scope)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=ProjectRequirementScopeSerializer)
    def put(self, request, pk):
        scope = self.get_object(pk)

        if not scope:
            return Response(
                {"success": False, "message": "Project requirement scope not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectRequirementScopeSerializer(scope, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Project requirement scope updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        scope = self.get_object(pk)

        if not scope:
            return Response(
                {"success": False, "message": "Project requirement scope not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        scope.delete()

        return Response(
            {"success": True, "message": "Project requirement scope deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# ProjectCandidate
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class ProjectCandidateListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        candidates = ProjectCandidate.objects.all().order_by("-id")
        serializer = ProjectCandidateSerializer(candidates, many=True)

        return Response(
            {
                "success": True,
                "message": "Project candidates fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(ProjectCandidateSerializer))
    def post(self, request):
        serializer = _create_serializer(ProjectCandidateSerializer, request)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Project candidate created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class ProjectCandidateRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return ProjectCandidate.objects.get(pk=pk)
        except ProjectCandidate.DoesNotExist:
            return None

    def get(self, request, pk):
        candidate = self.get_object(pk)

        if not candidate:
            return Response(
                {"success": False, "message": "Project candidate not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectCandidateSerializer(candidate)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=ProjectCandidateSerializer)
    def put(self, request, pk):
        candidate = self.get_object(pk)

        if not candidate:
            return Response(
                {"success": False, "message": "Project candidate not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectCandidateSerializer(candidate, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Project candidate updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        candidate = self.get_object(pk)

        if not candidate:
            return Response(
                {"success": False, "message": "Project candidate not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        candidate.delete()

        return Response(
            {"success": True, "message": "Project candidate deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# DisclosureRequest
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class DisclosureRequestListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        requests_qs = DisclosureRequest.objects.all().order_by("-created_at")
        serializer = DisclosureRequestSerializer(requests_qs, many=True)

        return Response(
            {
                "success": True,
                "message": "Disclosure requests fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(DisclosureRequestSerializer))
    def post(self, request):
        serializer = _create_serializer(DisclosureRequestSerializer, request, tenant_owned=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Disclosure request created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class DisclosureRequestRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return DisclosureRequest.objects.get(pk=pk)
        except DisclosureRequest.DoesNotExist:
            return None

    def get(self, request, pk):
        disclosure = self.get_object(pk)

        if not disclosure:
            return Response(
                {"success": False, "message": "Disclosure request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DisclosureRequestSerializer(disclosure)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=DisclosureRequestSerializer)
    def put(self, request, pk):
        disclosure = self.get_object(pk)

        if not disclosure:
            return Response(
                {"success": False, "message": "Disclosure request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = DisclosureRequestSerializer(disclosure, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Disclosure request updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        disclosure = self.get_object(pk)

        if not disclosure:
            return Response(
                {"success": False, "message": "Disclosure request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        disclosure.delete()

        return Response(
            {"success": True, "message": "Disclosure request deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# CandidateConsent — GET + POST only. A consent decision is not
# something this API lets a caller silently rewrite after the fact
# (see model docstring). Withdrawal/change = new consent record, not
# an edit to this one.
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class CandidateConsentListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        consents = CandidateConsent.objects.all().order_by("-decided_at")
        serializer = CandidateConsentSerializer(consents, many=True)

        return Response(
            {
                "success": True,
                "message": "Candidate consents fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(CandidateConsentSerializer))
    def post(self, request):
        serializer = _create_serializer(CandidateConsentSerializer, request)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Candidate consent recorded successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class CandidateConsentRetrieveAPIView(APIView):
    """GET only — consent decisions are not editable/deletable via this API."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return CandidateConsent.objects.get(pk=pk)
        except CandidateConsent.DoesNotExist:
            return None

    def get(self, request, pk):
        consent = self.get_object(pk)

        if not consent:
            return Response(
                {"success": False, "message": "Candidate consent not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CandidateConsentSerializer(consent)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------
# ProjectPlacement
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class ProjectPlacementListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        placements = ProjectPlacement.objects.all().order_by("-id")
        serializer = ProjectPlacementSerializer(placements, many=True)

        return Response(
            {
                "success": True,
                "message": "Project placements fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(ProjectPlacementSerializer))
    def post(self, request):
        serializer = _create_serializer(ProjectPlacementSerializer, request)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Project placement created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class ProjectPlacementRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return ProjectPlacement.objects.get(pk=pk)
        except ProjectPlacement.DoesNotExist:
            return None

    def get(self, request, pk):
        placement = self.get_object(pk)

        if not placement:
            return Response(
                {"success": False, "message": "Project placement not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectPlacementSerializer(placement)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=ProjectPlacementSerializer)
    def put(self, request, pk):
        placement = self.get_object(pk)

        if not placement:
            return Response(
                {"success": False, "message": "Project placement not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectPlacementSerializer(placement, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Project placement updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        placement = self.get_object(pk)

        if not placement:
            return Response(
                {"success": False, "message": "Project placement not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        placement.delete()

        return Response(
            {"success": True, "message": "Project placement deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# ProjectScopeLink
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class ProjectScopeLinkListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        links = ProjectScopeLink.objects.all().order_by("-created_at")
        serializer = ProjectScopeLinkSerializer(links, many=True)

        return Response(
            {
                "success": True,
                "message": "Project scope links fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=_single_or_bulk_schema(ProjectScopeLinkSerializer))
    def post(self, request):
        serializer = _create_serializer(ProjectScopeLinkSerializer, request)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Project scope link created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class ProjectScopeLinkRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return ProjectScopeLink.objects.get(pk=pk)
        except ProjectScopeLink.DoesNotExist:
            return None

    def get(self, request, pk):
        link = self.get_object(pk)

        if not link:
            return Response(
                {"success": False, "message": "Project scope link not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectScopeLinkSerializer(link)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=ProjectScopeLinkSerializer)
    def put(self, request, pk):
        link = self.get_object(pk)

        if not link:
            return Response(
                {"success": False, "message": "Project scope link not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectScopeLinkSerializer(link, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Project scope link updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        link = self.get_object(pk)

        if not link:
            return Response(
                {"success": False, "message": "Project scope link not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        link.delete()

        return Response(
            {"success": True, "message": "Project scope link deleted successfully."},
            status=status.HTTP_200_OK,
        )




# ---------------------------------------------------------------------
# ProjectMembership — no tenant field of its own (reached via project).
# POST is bulk-only: {tenant, assigned_by, memberships: [...]}. A
# duplicate (project, user) pair or a project from the wrong tenant is
# skipped and reported back, not a hard failure for the whole batch.
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class ProjectMembershipListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        memberships = ProjectMembership.objects.all().order_by("project", "user")
        serializer = ProjectMembershipSerializer(memberships, many=True)

        return Response(
            {
                "success": True,
                "message": "Project memberships fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=ProjectMembershipBulkCreateSerializer)
    def post(self, request):
        serializer = ProjectMembershipBulkCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tenant = serializer.validated_data["tenant"]
        assigned_by = serializer.validated_data["assigned_by"]
        items = serializer.validated_data["memberships"]

        created = []
        skipped = []

        with transaction.atomic():
            for item in items:
                project = item["project"]
                user = item["user"]

                if project.tenant_id != tenant.id:
                    skipped.append({
                        "project": project.id,
                        "user": user.id,
                        "reason": "Project does not belong to this tenant.",
                    })
                    continue

                if ProjectMembership.objects.filter(project=project, user=user).exists():
                    skipped.append({
                        "project": project.id,
                        "user": user.id,
                        "reason": "Membership already exists for this project and user.",
                    })
                    continue

                membership = ProjectMembership.objects.create(
                    project=project,
                    user=user,
                    role=item["role"],
                    scopes=item.get("scopes") or [],
                    effective_from=item.get("effective_from"),
                    effective_to=item.get("effective_to"),
                    entitlement=item.get("entitlement") or {},
                    assigned_by=assigned_by,
                )
                created.append(membership)

        return Response(
            {
                "success": True,
                "message": f"{len(created)} membership(s) created, {len(skipped)} skipped.",
                "data": {
                    "created": ProjectMembershipSerializer(created, many=True).data,
                    "skipped": skipped,
                },
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name='dispatch')
class ProjectMembershipRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return ProjectMembership.objects.get(pk=pk)
        except ProjectMembership.DoesNotExist:
            return None

    def get(self, request, pk):
        membership = self.get_object(pk)

        if not membership:
            return Response(
                {"success": False, "message": "Project membership not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectMembershipSerializer(membership)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=ProjectMembershipSerializer)
    def put(self, request, pk):
        membership = self.get_object(pk)

        if not membership:
            return Response(
                {"success": False, "message": "Project membership not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectMembershipSerializer(membership, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Project membership updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        membership = self.get_object(pk)

        if not membership:
            return Response(
                {"success": False, "message": "Project membership not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        membership.delete()

        return Response(
            {"success": True, "message": "Project membership deleted successfully."},
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name='dispatch')
class ProjectCreateWithMembershipsAPIView(APIView):
    """
    POST : Create one new Project, then bulk-create its initial
    ProjectMembership rows in the same request — mirrors
    TenantCombinedCreateAPIView's "parent + children in one call"
    shape, scoped to Project + ProjectMembership.

    The project is validated and created first; if that fails (missing
    required field, duplicate project_code for the tenant, etc.) the
    whole request fails with nothing created — no memberships are even
    attempted. Once the project exists, each membership item is
    created individually; a duplicate `user` appearing twice in the
    same request is skipped (not a hard failure) and reported back,
    same philosophy as ProjectMembershipListCreateAPIView's duplicate
    handling. `memberships` is optional — omitting it (or sending [])
    just creates the project on its own.
    """

    permission_classes = [AllowAny]

    @extend_schema(request=ProjectCreateWithMembershipsSerializer)
    def post(self, request):
        serializer = ProjectCreateWithMembershipsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated = serializer.validated_data
        assigned_by = validated["assigned_by"]
        items = validated.get("memberships") or []

        created = []
        skipped = []

        with transaction.atomic():
            project = Project.objects.create(**validated["project"])

            seen_users = set()
            for item in items:
                user = item["user"]

                if user.id in seen_users:
                    skipped.append({"user": user.id, "reason": "Duplicate user in this request."})
                    continue
                seen_users.add(user.id)

                membership = ProjectMembership.objects.create(
                    project=project,
                    user=user,
                    role=item["role"],
                    scopes=item.get("scopes") or [],
                    effective_from=item.get("effective_from"),
                    effective_to=item.get("effective_to"),
                    entitlement=item.get("entitlement") or {},
                    assigned_by=assigned_by,
                )
                created.append(membership)

        return Response(
            {
                "success": True,
                "message": f"Project created with {len(created)} membership(s), {len(skipped)} skipped.",
                "data": {
                    "project": ProjectSerializer(project).data,
                    "memberships": {
                        "created": ProjectMembershipSerializer(created, many=True).data,
                        "skipped": skipped,
                    },
                },
            },
            status=status.HTTP_201_CREATED,
        )




def _normalize_to_list(data):
    """
    Accept:
        {...}
    or:
        [{...}, {...}]

    Returns:
        list, was_single
    """

    if isinstance(data, list):
        return data, False

    if isinstance(data, dict):
        return [data], True

    return None, False


def _serialize_combined_legal_entities(queryset_or_instance, many=False):
    return TenantLegalEntityCombinedSerializer(
        queryset_or_instance,
        many=many,
    ).data


# ============================================================
# LIST + CREATE
# ============================================================


@method_decorator(csrf_exempt, name="dispatch")
class TenantLegalEntityCombinedListCreateAPIView(APIView):

    permission_classes = [AllowAny]

    # --------------------------------------------------------
    # GET ALL
    # --------------------------------------------------------

    def get(self, request):

        legal_entities = (
            TenantLegalEntity.objects
            .all()
            .select_related(
                "tenant",
                "requested_by",
                "reviewed_by",
            )
            .prefetch_related(
                "tax_registrations"
            )
            .order_by("-created_at")
        )

        serializer = TenantLegalEntityCombinedSerializer(
            legal_entities,
            many=True,
        )

        return Response(
            {
                "success": True,
                "message": (
                    "Tenant legal entities fetched successfully."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # --------------------------------------------------------
    # POST
    #
    # Supports:
    #   single legal entity
    #   multiple legal entities
    #
    # Each legal entity supports:
    #   single/multiple tax registrations
    # --------------------------------------------------------
    @extend_schema(
    request=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Create Tenant Legal Entities",
                value=[
                    {
                        "tenant": "tenant-uuid",
                        "registration_number": "REG-001",
                        "country_of_incorporation": "IN",
                        "incorporation_date": "2026-09-17",
                        "status": "PENDING",
                        "requested_by": 1,
                        "tax_registrations": [
                            {
                                "tax_type": "GST",
                                "country_code": "IN",
                                "tax_number": "36ABCDE1234F1Z5",
                                "status": "ACTIVE"
                            },
                            {
                                "tax_type": "PAN",
                                "country_code": "IN",
                                "tax_number": "ABCDE1234F",
                                "status": "ACTIVE"
                            }
                        ]
                    },
                    {
                        "tenant": "tenant-uuid",
                        "registration_number": "REG-002",
                        "country_of_incorporation": "AE",
                        "incorporation_date": "2025-05-10",
                        "status": "PENDING",
                        "requested_by": 1,
                        "tax_registrations": [
                            {
                                "tax_type": "VAT",
                                "country_code": "AE",
                                "tax_number": "100123456700003",
                                "status": "ACTIVE"
                            }
                        ]
                    }
                ],
                request_only=True,
            )
        ],
        responses={
            201: TenantLegalEntityCombinedSerializer(many=True)
        },
    )
    @transaction.atomic    
    def post(self, request):

        payload = request.data

        # ----------------------------------------------------
        # Accept either:
        #
        # {
        #     "legal_entities": [...]
        # }
        #
        # OR
        #
        # {
        #     "registration_number": "...",
        #     ...
        # }
        # ----------------------------------------------------

        if isinstance(payload, dict) and "legal_entities" in payload:
            payload = payload.get("legal_entities")

        legal_entities_data, was_single = _normalize_to_list(
            payload
        )

        if legal_entities_data is None:
            return Response(
                {
                    "success": False,
                    "message": (
                        "Payload must be an object or list "
                        "of legal entities."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not legal_entities_data:
            return Response(
                {
                    "success": False,
                    "message": (
                        "At least one legal entity is required."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_legal_entities = []

        # ====================================================
        # Loop legal entities
        # ====================================================

        for entity_index, entity_data in enumerate(
            legal_entities_data
        ):

            if not isinstance(entity_data, dict):

                transaction.set_rollback(True)

                return Response(
                    {
                        "success": False,
                        "message": (
                            "Each legal entity must be an object."
                        ),
                        "errors": {
                            "legal_entities": {
                                entity_index: (
                                    "Invalid legal entity object."
                                )
                            }
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            entity_data = entity_data.copy()

            tax_registrations = entity_data.pop(
                "tax_registrations",
                [],
            )

            # ------------------------------------------------
            # tax_registrations can be:
            #
            # {}
            # [{}, {}]
            # []
            # ------------------------------------------------

            if tax_registrations is None:
                tax_registrations = []

            elif isinstance(tax_registrations, dict):
                tax_registrations = [
                    tax_registrations
                ]

            elif not isinstance(
                tax_registrations,
                list,
            ):
                transaction.set_rollback(True)

                return Response(
                    {
                        "success": False,
                        "errors": {
                            "legal_entities": {
                                entity_index: {
                                    "tax_registrations": [
                                        (
                                            "Expected an object "
                                            "or list."
                                        )
                                    ]
                                }
                            }
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ------------------------------------------------
            # Create TenantLegalEntity
            # ------------------------------------------------

            legal_entity_serializer = (
                TenantLegalEntitySerializer(
                    data=entity_data
                )
            )

            if not legal_entity_serializer.is_valid():

                transaction.set_rollback(True)

                return Response(
                    {
                        "success": False,
                        "message": (
                            "Tenant legal entity validation failed."
                        ),
                        "errors": {
                            "legal_entities": {
                                entity_index: (
                                    legal_entity_serializer.errors
                                )
                            }
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            legal_entity = (
                legal_entity_serializer.save()
            )

            # ------------------------------------------------
            # Create children
            # ------------------------------------------------

            for tax_index, tax_data in enumerate(
                tax_registrations
            ):

                if not isinstance(tax_data, dict):

                    transaction.set_rollback(True)

                    return Response(
                        {
                            "success": False,
                            "errors": {
                                "legal_entities": {
                                    entity_index: {
                                        "tax_registrations": {
                                            tax_index: (
                                                "Invalid object."
                                            )
                                        }
                                    }
                                }
                            },
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                tax_data = tax_data.copy()

                # Never trust parent FK from frontend.
                tax_data.pop(
                    "legal_entity",
                    None,
                )

                # Child must belong to same tenant
                # as parent legal entity.
                tax_data.pop(
                    "tenant",
                    None,
                )

                tax_data["legal_entity"] = (
                    legal_entity.pk
                )

                tax_data["tenant"] = (
                    legal_entity.tenant_id
                )

                tax_serializer = (
                    TenantTaxRegistrationSerializer(
                        data=tax_data
                    )
                )

                if not tax_serializer.is_valid():

                    transaction.set_rollback(True)

                    return Response(
                        {
                            "success": False,
                            "message": (
                                "Tax registration "
                                "validation failed."
                            ),
                            "errors": {
                                "legal_entities": {
                                    entity_index: {
                                        "tax_registrations": {
                                            tax_index: (
                                                tax_serializer.errors
                                            )
                                        }
                                    }
                                }
                            },
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                tax_serializer.save()

            created_legal_entities.append(
                legal_entity
            )

        # ====================================================
        # Response
        # ====================================================

        created_ids = [
            obj.pk
            for obj in created_legal_entities
        ]

        result = (
            TenantLegalEntity.objects
            .filter(pk__in=created_ids)
            .select_related(
                "tenant",
                "requested_by",
                "reviewed_by",
            )
            .prefetch_related(
                "tax_registrations"
            )
        )

        serializer = TenantLegalEntityCombinedSerializer(
            result,
            many=True,
        )

        return Response(
            {
                "success": True,
                "message": (
                    "Tenant legal entities and tax "
                    "registrations created successfully."
                ),
                "data": (
                    serializer.data[0]
                    if was_single
                    else serializer.data
                ),
            },
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# RETRIEVE + UPDATE
# ============================================================


@method_decorator(csrf_exempt, name="dispatch")
class TenantLegalEntityCombinedRetrieveUpdateAPIView(APIView):

    permission_classes = [AllowAny]

    def get_object(self, pk):

        try:
            return (TenantLegalEntity.objects.select_related("tenant","requested_by","reviewed_by",
                                                         ).prefetch_related("tax_registrations").get(pk=pk))

        except TenantLegalEntity.DoesNotExist:
            return None

    # --------------------------------------------------------
    # GET BY LEGAL ENTITY ID
    # --------------------------------------------------------

    def get(self, request, pk):

        legal_entity = self.get_object(pk)

        if not legal_entity:

            return Response(
                {
                    "success": False,
                    "message": (
                        "Tenant legal entity not found."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantLegalEntityCombinedSerializer(legal_entity)

        return Response(
            {
                "success": True,
                "message": (
                    "Tenant legal entity fetched successfully."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # --------------------------------------------------------
    # PUT
    #
    # Expected:
    #
    # {
    #   "registration_number": "...",
    #   ...
    #
    #   "tax_registrations": {
    #
    #       "updated": [
    #           {
    #               "id": "...",
    #               "tax_number": "..."
    #           }
    #       ],
    #
    #       "deleted_ids": [
    #           "...",
    #           "..."
    #       ],
    #
    #       "new": [
    #           {
    #               "tax_type": "GST",
    #               ...
    #           }
    #       ]
    #   }
    # }
    #
    # --------------------------------------------------------
    @extend_schema(
    request=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Update Tenant Legal Entity",
                value={
                    "registration_number": "REG-001-UPDATED",
                    "country_of_incorporation": "IN",
                    "incorporation_date": "2026-09-17",
                    "status": "ACTIVE",

                    "tax_registrations": {
                        "updated": [
                            {
                                "id": "tax-registration-uuid-1",
                                "tax_type": "GST",
                                "country_code": "IN",
                                "tax_number": "UPDATED-GST-001",
                                "status": "ACTIVE"
                            },
                            {
                                "id": "tax-registration-uuid-2",
                                "tax_number": "UPDATED-TAX-002"
                            }
                        ],

                        "deleted_ids": [
                            "tax-registration-uuid-3",
                            "tax-registration-uuid-4"
                        ],

                        "new": [
                            {
                                "tax_type": "GST",
                                "country_code": "IN",
                                "tax_number": "NEW-GST-001",
                                "status": "ACTIVE"
                            },
                            {
                                "tax_type": "VAT",
                                "country_code": "AE",
                                "tax_number": "NEW-VAT-001",
                                "status": "ACTIVE"
                            }
                        ]
                    }
                },
                request_only=True,
            )
        ],
        responses={
            200: TenantLegalEntityCombinedSerializer
        },
    )
    @transaction.atomic    
    def put(self, request, pk):

        legal_entity = self.get_object(pk)

        if not legal_entity:

            return Response(
                {
                    "success": False,
                    "message": (
                        "Tenant legal entity not found."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()

        tax_operations = data.pop(
            "tax_registrations",
            {},
        )

        # Tenant cannot be changed through update.
        data.pop("tenant", None)

        # ID cannot be changed.
        data.pop("id", None)

        # ====================================================
        # Validate tax operation structure
        # ====================================================

        if tax_operations is None:
            tax_operations = {}

        if not isinstance(tax_operations, dict):

            return Response(
                {
                    "success": False,
                    "errors": {
                        "tax_registrations": [
                            (
                                "Expected an object containing "
                                "updated, deleted_ids and new."
                            )
                        ]
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_records = tax_operations.get(
            "updated",
            [],
        )

        deleted_ids = tax_operations.get(
            "deleted_ids",
            [],
        )

        new_records = tax_operations.get(
            "new",
            [],
        )

        if not isinstance(updated_records, list):

            return Response(
                {
                    "success": False,
                    "errors": {
                        "tax_registrations.updated": [
                            "Expected a list."
                        ]
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(deleted_ids, list):

            return Response(
                {
                    "success": False,
                    "errors": {
                        "tax_registrations.deleted_ids": [
                            "Expected a list."
                        ]
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(new_records, list):

            return Response(
                {
                    "success": False,
                    "errors": {
                        "tax_registrations.new": [
                            "Expected a list."
                        ]
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ====================================================
        # Update TenantLegalEntity
        # ====================================================

        legal_entity_serializer = (
            TenantLegalEntitySerializer(
                legal_entity,
                data=data,
                partial=True,
            )
        )

        if not legal_entity_serializer.is_valid():

            return Response(
                {
                    "success": False,
                    "errors": (
                        legal_entity_serializer.errors
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        legal_entity = (
            legal_entity_serializer.save()
        )

        # ====================================================
        # A. UPDATE existing TenantTaxRegistration
        # ====================================================

        for index, tax_data in enumerate(
            updated_records
        ):

            if not isinstance(tax_data, dict):

                transaction.set_rollback(True)

                return Response(
                    {
                        "success": False,
                        "errors": {
                            "tax_registrations.updated": {
                                index: "Invalid object."
                            }
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tax_data = tax_data.copy()

            tax_id = tax_data.pop(
                "id",
                None,
            )

            if not tax_id:

                transaction.set_rollback(True)

                return Response(
                    {
                        "success": False,
                        "errors": {
                            "tax_registrations.updated": {
                                index: {
                                    "id": [
                                        "This field is required."
                                    ]
                                }
                            }
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # IMPORTANT:
            # only fetch child belonging to this parent.
            try:
                tax_registration = (
                    TenantTaxRegistration.objects.get(
                        pk=tax_id,
                        legal_entity=legal_entity,
                    )
                )

            except TenantTaxRegistration.DoesNotExist:

                transaction.set_rollback(True)

                return Response(
                    {
                        "success": False,
                        "errors": {
                            "tax_registrations.updated": {
                                index: {
                                    "id": [
                                        (
                                            "Tax registration not "
                                            "found for this legal "
                                            "entity."
                                        )
                                    ]
                                }
                            }
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Prevent moving child.
            tax_data.pop(
                "legal_entity",
                None,
            )

            tax_data.pop(
                "tenant",
                None,
            )

            tax_serializer = (
                TenantTaxRegistrationSerializer(
                    tax_registration,
                    data=tax_data,
                    partial=True,
                )
            )

            if not tax_serializer.is_valid():

                transaction.set_rollback(True)

                return Response(
                    {
                        "success": False,
                        "errors": {
                            "tax_registrations.updated": {
                                index: (
                                    tax_serializer.errors
                                )
                            }
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tax_serializer.save()

        # ====================================================
        # B. DELETE TenantTaxRegistration
        # ====================================================

        if deleted_ids:

            existing_delete_ids = set(
                str(value)
                for value in (
                    TenantTaxRegistration.objects
                    .filter(
                        pk__in=deleted_ids,
                        legal_entity=legal_entity,
                    )
                    .values_list(
                        "pk",
                        flat=True,
                    )
                )
            )

            requested_delete_ids = set(
                str(value)
                for value in deleted_ids
            )

            invalid_delete_ids = (
                requested_delete_ids
                - existing_delete_ids
            )

            if invalid_delete_ids:

                transaction.set_rollback(True)

                return Response(
                    {
                        "success": False,
                        "errors": {
                            "tax_registrations.deleted_ids": [
                                (
                                    "These tax registration IDs "
                                    "do not belong to this legal "
                                    "entity: "
                                    + ", ".join(
                                        invalid_delete_ids
                                    )
                                )
                            ]
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            TenantTaxRegistration.objects.filter(
                pk__in=deleted_ids,
                legal_entity=legal_entity,
            ).delete()

        # ====================================================
        # C. CREATE new TenantTaxRegistration
        # ====================================================

        for index, tax_data in enumerate(
            new_records
        ):

            if not isinstance(tax_data, dict):

                transaction.set_rollback(True)

                return Response(
                    {
                        "success": False,
                        "errors": {
                            "tax_registrations.new": {
                                index: "Invalid object."
                            }
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tax_data = tax_data.copy()

            # Never accept these from frontend.
            tax_data.pop(
                "id",
                None,
            )

            tax_data.pop(
                "legal_entity",
                None,
            )

            tax_data.pop(
                "tenant",
                None,
            )

            # Force correct parent and tenant.
            tax_data["legal_entity"] = (
                legal_entity.pk
            )

            tax_data["tenant"] = (
                legal_entity.tenant_id
            )

            tax_serializer = (
                TenantTaxRegistrationSerializer(
                    data=tax_data
                )
            )

            if not tax_serializer.is_valid():

                transaction.set_rollback(True)

                return Response(
                    {
                        "success": False,
                        "errors": {
                            "tax_registrations.new": {
                                index: (
                                    tax_serializer.errors
                                )
                            }
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tax_serializer.save()

        # ====================================================
        # Final response
        # ====================================================

        legal_entity = (
            TenantLegalEntity.objects
            .select_related(
                "tenant",
                "requested_by",
                "reviewed_by",
            )
            .prefetch_related(
                "tax_registrations"
            )
            .get(pk=legal_entity.pk)
        )

        serializer = TenantLegalEntityCombinedSerializer(
            legal_entity
        )

        return Response(
            {
                "success": True,
                "message": (
                    "Tenant legal entity and tax "
                    "registrations updated successfully."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# DELETE SINGLE / MULTIPLE
# ============================================================

@method_decorator(csrf_exempt, name="dispatch")
class TenantLegalEntityCombinedDeleteAPIView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        request=inline_serializer(
            name="TenantLegalEntityBulkDeleteRequest",
            fields={
                "ids": serializers.ListField(
                    child=serializers.IntegerField(),
                    allow_empty=False,
                ),
            },
        ),
        responses={
            200: OpenApiTypes.OBJECT,
        },
    )
    @transaction.atomic
    def post(self, request):

        ids = request.data.get("ids", [])

        if not isinstance(ids, list):
            return Response(
                {
                    "success": False,
                    "message": "ids must be a list.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not ids:
            return Response(
                {
                    "success": False,
                    "message": (
                        "At least one TenantLegalEntity "
                        "ID is required."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        legal_entities = TenantLegalEntity.objects.filter(
            pk__in=ids
        )

        existing_ids = set(
            legal_entities.values_list(
                "pk",
                flat=True,
            )
        )

        requested_ids = set(ids)

        invalid_ids = requested_ids - existing_ids

        if invalid_ids:
            return Response(
                {
                    "success": False,
                    "message": (
                        "One or more TenantLegalEntity "
                        "records were not found."
                    ),
                    "invalid_ids": list(invalid_ids),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        deleted_ids = list(existing_ids)

        # TenantTaxRegistration children are automatically
        # deleted because of on_delete=models.CASCADE.
        legal_entities.delete()

        return Response(
            {
                "success": True,
                "message": (
                    "Tenant legal entities and their "
                    "tax registrations deleted successfully."
                ),
                "data": {
                    "deleted_ids": deleted_ids,
                    "deleted_count": len(deleted_ids),
                },
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class ProjectRequirementCombinedListCreateAPIView(APIView):

    permission_classes = [AllowAny]

    # ========================================================
    # GET ALL
    # ========================================================

    def get(self, request):

        requirements = (
            ProjectRequirement.objects
            .all()
            .select_related(
                "project",
                "tenant",
            )
            .prefetch_related(
                "requirement_scopes"
            )
            .order_by("-created_at")
        )

        serializer = ProjectRequirementCombinedSerializer(
            requirements,
            many=True,
        )

        return Response(
            {
                "success": True,
                "message": (
                    "Project requirements fetched successfully."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # ========================================================
    # POST
    # Single / Multiple ProjectRequirement
    # Each can contain multiple ProjectRequirementScope
    # ========================================================

    @extend_schema(
        request=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Create Project Requirements",
                value=[
                    {
                        "tenant": 1,
                        "project": 1,
                        "role_code": 34,
                        "required_count": 5,
                        "minimum_experience_years": 3,
                        "mandatory": True,
                        "remarks": "NDT experience preferred",
                        "requirement_scopes": [
                            {
                                "scope_catalog": 10
                            },
                            {
                                "scope_catalog": 11
                            }
                        ]
                    },
                    {
                        "tenant": 1,
                        "project": 1,
                        "role_code": 35,
                        "required_count": 2,
                        "minimum_experience_years": 5,
                        "mandatory": True,
                        "remarks": "",
                        "requirement_scopes": [
                            {
                                "scope_catalog": 15
                            }
                        ]
                    }
                ],
                request_only=True,
            )
        ],
        responses={
            201: ProjectRequirementCombinedSerializer(
                many=True
            )
        },
    )
    @transaction.atomic
    def post(self, request):

        payload = request.data

        # Accept single object OR list
        if isinstance(payload, dict):
            requirements_data = [payload]
            was_single = True

        elif isinstance(payload, list):
            requirements_data = payload
            was_single = False

        else:
            return Response(
                {
                    "success": False,
                    "message": (
                        "Payload must be an object or list "
                        "of project requirements."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not requirements_data:
            return Response(
                {
                    "success": False,
                    "message": (
                        "At least one project requirement "
                        "is required."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_requirements = []

        # ====================================================
        # LOOP REQUIREMENTS
        # ====================================================

        for req_index, requirement_data in enumerate(
            requirements_data
        ):

            if not isinstance(requirement_data, dict):

                transaction.set_rollback(True)

                return Response(
                    {
                        "success": False,
                        "errors": {
                            "requirements": {
                                req_index: (
                                    "Invalid requirement object."
                                )
                            }
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            requirement_data = requirement_data.copy()

            requirement_scopes = requirement_data.pop(
                "requirement_scopes",
                [],
            )

            # Allow one object also
            if requirement_scopes is None:
                requirement_scopes = []

            elif isinstance(requirement_scopes, dict):
                requirement_scopes = [
                    requirement_scopes
                ]

            elif not isinstance(
                requirement_scopes,
                list,
            ):

                transaction.set_rollback(True)

                return Response(
                    {
                        "success": False,
                        "errors": {
                            "requirements": {
                                req_index: {
                                    "requirement_scopes": [
                                        (
                                            "Expected an object "
                                            "or list."
                                        )
                                    ]
                                }
                            }
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # =================================================
            # CREATE ProjectRequirement
            # =================================================

            requirement_serializer = (
                ProjectRequirementSerializer(
                    data=requirement_data
                )
            )

            if not requirement_serializer.is_valid():

                transaction.set_rollback(True)

                return Response(
                    {
                        "success": False,
                        "message": (
                            "Project requirement validation "
                            "failed."
                        ),
                        "errors": {
                            "requirements": {
                                req_index: (
                                    requirement_serializer.errors
                                )
                            }
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            requirement = requirement_serializer.save()

            # =================================================
            # CREATE ProjectRequirementScope CHILDREN
            # =================================================

            for scope_index, scope_data in enumerate(
                requirement_scopes
            ):

                if not isinstance(scope_data, dict):

                    transaction.set_rollback(True)

                    return Response(
                        {
                            "success": False,
                            "errors": {
                                "requirements": {
                                    req_index: {
                                        "requirement_scopes": {
                                            scope_index: (
                                                "Invalid object."
                                            )
                                        }
                                    }
                                }
                            },
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                scope_data = scope_data.copy()

                # Do not trust parent from frontend
                scope_data.pop(
                    "requirement",
                    None,
                )

                scope_data["requirement"] = (
                    requirement.pk
                )

                scope_serializer = (
                    ProjectRequirementScopeSerializer(
                        data=scope_data
                    )
                )

                if not scope_serializer.is_valid():

                    transaction.set_rollback(True)

                    return Response(
                        {
                            "success": False,
                            "message": (
                                "Project requirement scope "
                                "validation failed."
                            ),
                            "errors": {
                                "requirements": {
                                    req_index: {
                                        "requirement_scopes": {
                                            scope_index: (
                                                scope_serializer.errors
                                            )
                                        }
                                    }
                                }
                            },
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                scope_serializer.save()

            created_requirements.append(
                requirement
            )

        # ====================================================
        # RESPONSE
        # ====================================================

        created_ids = [
            obj.pk
            for obj in created_requirements
        ]

        result = (
            ProjectRequirement.objects
            .filter(pk__in=created_ids)
            .prefetch_related(
                "requirement_scopes"
            )
        )

        serializer = ProjectRequirementCombinedSerializer(
            result,
            many=True,
        )

        return Response(
            {
                "success": True,
                "message": (
                    "Project requirements and scopes "
                    "created successfully."
                ),
                "data": (
                    serializer.data[0]
                    if was_single
                    else serializer.data
                ),
            },
            status=status.HTTP_201_CREATED,
        )



@method_decorator(csrf_exempt, name="dispatch")
class ProjectRequirementCombinedRetrieveUpdateAPIView(
    APIView
):

    permission_classes = [AllowAny]

    def get_object(self, pk):

        try:
            return (
                ProjectRequirement.objects
                .select_related(
                    "project",
                    "tenant",
                )
                .prefetch_related(
                    "requirement_scopes"
                )
                .get(pk=pk)
            )

        except ProjectRequirement.DoesNotExist:
            return None

    # ========================================================
    # GET BY ID
    # ========================================================

    def get(self, request, pk):

        requirement = self.get_object(pk)

        if not requirement:

            return Response(
                {
                    "success": False,
                    "message": (
                        "Project requirement not found."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectRequirementCombinedSerializer(
            requirement
        )

        return Response(
            {
                "success": True,
                "message": (
                    "Project requirement fetched "
                    "successfully."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # ========================================================
    # PUT
    # ========================================================

    @extend_schema(
        request=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Update Project Requirement",
                value={
                    "role_code": 34,
                    "required_count": 10,
                    "minimum_experience_years": 5,
                    "mandatory": True,
                    "remarks": "Updated requirement",
                    "requirement_scopes": {
                        "updated": [
                        {
                            "id": 1,
                            "scope_catalog": 20
                        },
                        {
                            "id": 2,
                            "scope_catalog": 21
                        }
                        ],
                        "deleted_ids": [
                        3,
                        4
                        ],
                        "new": [
                        {
                            "scope_catalog": 25
                        },
                        {
                            "scope_catalog": 26
                        }
                        ]
                    }
                    },
                request_only=True,
            )
        ],
        responses={
            200: ProjectRequirementCombinedSerializer
        },
    )
    @transaction.atomic
    def put(self, request, pk):

        requirement = self.get_object(pk)

        if not requirement:

            return Response(
                {
                    "success": False,
                    "message": (
                        "Project requirement not found."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()

        scope_operations = data.pop(
            "requirement_scopes",
            {},
        )

        # Don't allow ID changes
        data.pop("id", None)

        # ====================================================
        # VALIDATE OPERATION STRUCTURE
        # ====================================================

        if scope_operations is None:
            scope_operations = {}

        if not isinstance(scope_operations, dict):

            return Response(
                {
                    "success": False,
                    "errors": {
                        "requirement_scopes": [
                            (
                                "Expected an object containing "
                                "updated, deleted_ids and new."
                            )
                        ]
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_records = scope_operations.get(
            "updated",
            [],
        )

        deleted_ids = scope_operations.get(
            "deleted_ids",
            [],
        )

        new_records = scope_operations.get(
            "new",
            [],
        )

        if not isinstance(updated_records, list):

            return Response(
                {
                    "success": False,
                    "errors": {
                        "requirement_scopes.updated": [
                            "Expected a list."
                        ]
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(deleted_ids, list):

            return Response(
                {
                    "success": False,
                    "errors": {
                        "requirement_scopes.deleted_ids": [
                            "Expected a list."
                        ]
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(new_records, list):

            return Response(
                {
                    "success": False,
                    "errors": {
                        "requirement_scopes.new": [
                            "Expected a list."
                        ]
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ====================================================
        # UPDATE PARENT
        # ====================================================

        requirement_serializer = (
            ProjectRequirementSerializer(
                requirement,
                data=data,
                partial=True,
            )
        )

        if not requirement_serializer.is_valid():

            return Response(
                {
                    "success": False,
                    "errors": (
                        requirement_serializer.errors
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        requirement = requirement_serializer.save()

        # ====================================================
        # A. UPDATE EXISTING SCOPES
        # ====================================================

        for index, scope_data in enumerate(
            updated_records
        ):

            if not isinstance(scope_data, dict):

                transaction.set_rollback(True)

                return Response(
                    {
                        "success": False,
                        "errors": {
                            "requirement_scopes.updated": {
                                index: "Invalid object."
                            }
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            scope_data = scope_data.copy()

            scope_record_id = scope_data.pop(
                "id",
                None,
            )

            if not scope_record_id:

                transaction.set_rollback(True)

                return Response(
                    {
                        "success": False,
                        "errors": {
                            "requirement_scopes.updated": {
                                index: {
                                    "id": [
                                        "This field is required."
                                    ]
                                }
                            }
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                requirement_scope = (
                    ProjectRequirementScope.objects.get(
                        pk=scope_record_id,
                        requirement=requirement,
                    )
                )

            except ProjectRequirementScope.DoesNotExist:

                transaction.set_rollback(True)

                return Response(
                    {
                        "success": False,
                        "errors": {
                            "requirement_scopes.updated": {
                                index: {
                                    "id": [
                                        (
                                            "Project requirement "
                                            "scope not found for "
                                            "this requirement."
                                        )
                                    ]
                                }
                            }
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Cannot move child to another parent
            scope_data.pop(
                "requirement",
                None,
            )

            scope_serializer = (
                ProjectRequirementScopeSerializer(
                    requirement_scope,
                    data=scope_data,
                    partial=True,
                )
            )

            if not scope_serializer.is_valid():

                transaction.set_rollback(True)

                return Response(
                    {
                        "success": False,
                        "errors": {
                            "requirement_scopes.updated": {
                                index: (
                                    scope_serializer.errors
                                )
                            }
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            scope_serializer.save()

        # ====================================================
        # B. DELETE SCOPES
        # ====================================================

        if deleted_ids:

            existing_delete_ids = set(
                ProjectRequirementScope.objects
                .filter(
                    pk__in=deleted_ids,
                    requirement=requirement,
                )
                .values_list(
                    "pk",
                    flat=True,
                )
            )

            requested_delete_ids = set(
                deleted_ids
            )

            invalid_delete_ids = (
                requested_delete_ids
                - existing_delete_ids
            )

            if invalid_delete_ids:

                transaction.set_rollback(True)

                return Response(
                    {
                        "success": False,
                        "errors": {
                            "requirement_scopes.deleted_ids": [
                                (
                                    "These IDs do not belong "
                                    "to this project requirement: "
                                    + ", ".join(
                                        map(
                                            str,
                                            invalid_delete_ids,
                                        )
                                    )
                                )
                            ]
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            ProjectRequirementScope.objects.filter(
                pk__in=deleted_ids,
                requirement=requirement,
            ).delete()

        # ====================================================
        # C. CREATE NEW SCOPES
        # ====================================================

        for index, scope_data in enumerate(
            new_records
        ):

            if not isinstance(scope_data, dict):

                transaction.set_rollback(True)

                return Response(
                    {
                        "success": False,
                        "errors": {
                            "requirement_scopes.new": {
                                index: "Invalid object."
                            }
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            scope_data = scope_data.copy()

            scope_data.pop(
                "id",
                None,
            )

            scope_data.pop(
                "requirement",
                None,
            )

            scope_data["requirement"] = (
                requirement.pk
            )

            scope_serializer = (
                ProjectRequirementScopeSerializer(
                    data=scope_data
                )
            )

            if not scope_serializer.is_valid():

                transaction.set_rollback(True)

                return Response(
                    {
                        "success": False,
                        "errors": {
                            "requirement_scopes.new": {
                                index: (
                                    scope_serializer.errors
                                )
                            }
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            scope_serializer.save()

        # ====================================================
        # FINAL RESPONSE
        # ====================================================

        requirement = (
            ProjectRequirement.objects
            .prefetch_related(
                "requirement_scopes"
            )
            .get(pk=requirement.pk)
        )

        serializer = ProjectRequirementCombinedSerializer(
            requirement
        )

        return Response(
            {
                "success": True,
                "message": (
                    "Project requirement and scopes "
                    "updated successfully."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class ProjectRequirementCombinedDeleteAPIView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        request=inline_serializer(
            name="ProjectRequirementBulkDeleteRequest",
            fields={
                "ids": serializers.ListField(
                    child=serializers.IntegerField(),
                    allow_empty=False,
                ),
            },
        ),
        responses={
            200: OpenApiTypes.OBJECT,
        },
    )
    @transaction.atomic
    def post(self, request):

        ids = request.data.get(
            "ids",
            [],
        )

        if not isinstance(ids, list):

            return Response(
                {
                    "success": False,
                    "message": "ids must be a list.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not ids:

            return Response(
                {
                    "success": False,
                    "message": (
                        "At least one ProjectRequirement "
                        "ID is required."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        requirements = (
            ProjectRequirement.objects
            .filter(pk__in=ids)
        )

        existing_ids = set(
            requirements.values_list(
                "pk",
                flat=True,
            )
        )

        requested_ids = set(ids)

        invalid_ids = (
            requested_ids
            - existing_ids
        )

        if invalid_ids:

            return Response(
                {
                    "success": False,
                    "message": (
                        "One or more ProjectRequirement "
                        "records were not found."
                    ),
                    "invalid_ids": list(
                        invalid_ids
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        deleted_ids = list(
            existing_ids
        )

        # ProjectRequirementScope children will be
        # deleted automatically if requirement FK
        # uses on_delete=models.CASCADE.
        requirements.delete()

        return Response(
            {
                "success": True,
                "message": (
                    "Project requirements and their "
                    "scopes deleted successfully."
                ),
                "data": {
                    "deleted_ids": deleted_ids,
                    "deleted_count": len(
                        deleted_ids
                    ),
                },
            },
            status=status.HTTP_200_OK,
        )





