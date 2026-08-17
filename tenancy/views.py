from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema, OpenApiParameter
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
    
    @extend_schema(request=TenantOperationSerializer)
    def post(self, request):
        serializer = TenantOperationSerializer(data=request.data)

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

    @extend_schema(request=OrganizationSerializer)
    def post(self, request):
        serializer = OrganizationSerializer(data=request.data)

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

    @extend_schema(request=TenantLegalEntitySerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantLegalEntitySerializer(data=data)

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
    GET    : Get tenant legal entity by public_id
    PUT    : Update tenant legal entity (partial)
    DELETE : Delete tenant legal entity
    """

    permission_classes = [AllowAny]

    def get_object(self, public_id):
        try:
            return TenantLegalEntity.objects.get(public_id=public_id)
        except TenantLegalEntity.DoesNotExist:
            return None

    def get(self, request, public_id):
        entity = self.get_object(public_id)

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
    def put(self, request, public_id):
        entity = self.get_object(public_id)

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

    def delete(self, request, public_id):
        entity = self.get_object(public_id)

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

    @extend_schema(request=TenantTaxRegistrationSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantTaxRegistrationSerializer(data=data)

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
    GET    : Get tenant tax registration by public_id
    PUT    : Update tenant tax registration (partial)
    DELETE : Delete tenant tax registration
    """

    permission_classes = [AllowAny]

    def get_object(self, public_id):
        try:
            return TenantTaxRegistration.objects.get(public_id=public_id)
        except TenantTaxRegistration.DoesNotExist:
            return None

    def get(self, request, public_id):
        registration = self.get_object(public_id)

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
    def put(self, request, public_id):
        registration = self.get_object(public_id)

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

    def delete(self, request, public_id):
        registration = self.get_object(public_id)

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

    @extend_schema(request=TenantDomainSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantDomainSerializer(data=data)

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
    GET    : Get tenant domain by public_id
    PUT    : Update tenant domain (partial)
    DELETE : Delete tenant domain
    """

    permission_classes = [AllowAny]

    def get_object(self, public_id):
        try:
            return TenantDomain.objects.get(public_id=public_id)
        except TenantDomain.DoesNotExist:
            return None

    def get(self, request, public_id):
        domain = self.get_object(public_id)

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
    def put(self, request, public_id):
        domain = self.get_object(public_id)

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

    def delete(self, request, public_id):
        domain = self.get_object(public_id)

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


@method_decorator(csrf_exempt, name='dispatch')
class TenantIndustryListCreateAPIView(APIView):
    """
    GET  : Get all tenant industries
    POST : Create a new tenant industry
    """

    permission_classes = [AllowAny]

    def get(self, request):
        industries = TenantIndustry.objects.all().order_by("-created_at")
        serializer = TenantIndustrySerializer(industries, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant industries fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=TenantIndustrySerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantIndustrySerializer(data=data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant industry created successfully.",
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
class TenantIndustryRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Get tenant industry by public_id
    PUT    : Update tenant industry (partial)
    DELETE : Delete tenant industry
    """

    permission_classes = [AllowAny]

    def get_object(self, public_id):
        try:
            return TenantIndustry.objects.get(public_id=public_id)
        except TenantIndustry.DoesNotExist:
            return None

    def get(self, request, public_id):
        industry = self.get_object(public_id)

        if not industry:
            return Response(
                {
                    "success": False,
                    "message": "Tenant industry not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantIndustrySerializer(industry)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=TenantIndustrySerializer)
    def put(self, request, public_id):
        industry = self.get_object(public_id)

        if not industry:
            return Response(
                {
                    "success": False,
                    "message": "Tenant industry not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantIndustrySerializer(industry, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant industry updated successfully.",
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

    def delete(self, request, public_id):
        industry = self.get_object(public_id)

        if not industry:
            return Response(
                {
                    "success": False,
                    "message": "Tenant industry not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        industry.delete()

        return Response(
            {
                "success": True,
                "message": "Tenant industry deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantScope
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantScopeListCreateAPIView(APIView):
    """
    GET  : Get all tenant scopes
    POST : Create a new tenant scope
    """

    permission_classes = [AllowAny]

    def get(self, request):
        scopes = TenantScope.objects.all().order_by("-created_at")
        serializer = TenantScopeSerializer(scopes, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant scopes fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=TenantScopeSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantScopeSerializer(data=data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant scope created successfully.",
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
class TenantScopeRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Get tenant scope by public_id
    PUT    : Update tenant scope (partial)
    DELETE : Delete tenant scope
    """

    permission_classes = [AllowAny]

    def get_object(self, public_id):
        try:
            return TenantScope.objects.get(public_id=public_id)
        except TenantScope.DoesNotExist:
            return None

    def get(self, request, public_id):
        scope = self.get_object(public_id)

        if not scope:
            return Response(
                {
                    "success": False,
                    "message": "Tenant scope not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantScopeSerializer(scope)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=TenantScopeSerializer)
    def put(self, request, public_id):
        scope = self.get_object(public_id)

        if not scope:
            return Response(
                {
                    "success": False,
                    "message": "Tenant scope not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantScopeSerializer(scope, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant scope updated successfully.",
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

    def delete(self, request, public_id):
        scope = self.get_object(public_id)

        if not scope:
            return Response(
                {
                    "success": False,
                    "message": "Tenant scope not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        scope.delete()

        return Response(
            {
                "success": True,
                "message": "Tenant scope deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# TenantBusinessUnit
# ---------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class TenantBusinessUnitListCreateAPIView(APIView):
    """
    GET  : Get all tenant business units
    POST : Create a new tenant business unit
    """

    permission_classes = [AllowAny]

    def get(self, request):
        units = TenantBusinessUnit.objects.all().order_by("-created_at")
        serializer = TenantBusinessUnitSerializer(units, many=True)

        return Response(
            {
                "success": True,
                "message": "Tenant business units fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=TenantBusinessUnitSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantBusinessUnitSerializer(data=data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant business unit created successfully.",
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
class TenantBusinessUnitRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Get tenant business unit by public_id
    PUT    : Update tenant business unit (partial)
    DELETE : Delete tenant business unit
    """

    permission_classes = [AllowAny]

    def get_object(self, public_id):
        try:
            return TenantBusinessUnit.objects.get(public_id=public_id)
        except TenantBusinessUnit.DoesNotExist:
            return None

    def get(self, request, public_id):
        unit = self.get_object(public_id)

        if not unit:
            return Response(
                {
                    "success": False,
                    "message": "Tenant business unit not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantBusinessUnitSerializer(unit)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=TenantBusinessUnitSerializer)
    def put(self, request, public_id):
        unit = self.get_object(public_id)

        if not unit:
            return Response(
                {
                    "success": False,
                    "message": "Tenant business unit not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data.pop("tenant", None)

        serializer = TenantBusinessUnitSerializer(unit, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Tenant business unit updated successfully.",
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

    def delete(self, request, public_id):
        unit = self.get_object(public_id)

        if not unit:
            return Response(
                {
                    "success": False,
                    "message": "Tenant business unit not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        unit.delete()

        return Response(
            {
                "success": True,
                "message": "Tenant business unit deleted successfully.",
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

    @extend_schema(request=TenantLocationSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantLocationSerializer(data=data)

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
    GET    : Get tenant location by public_id
    PUT    : Update tenant location (partial)
    DELETE : Delete tenant location
    """

    permission_classes = [AllowAny]

    def get_object(self, public_id):
        try:
            return TenantLocation.objects.get(public_id=public_id)
        except TenantLocation.DoesNotExist:
            return None

    def get(self, request, public_id):
        location = self.get_object(public_id)

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
    def put(self, request, public_id):
        location = self.get_object(public_id)

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

    def delete(self, request, public_id):
        location = self.get_object(public_id)

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

    @extend_schema(request=TenantAuthorisedRepresentativeSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantAuthorisedRepresentativeSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantAuthorisedRepresentative.objects.get(public_id=public_id)
        except TenantAuthorisedRepresentative.DoesNotExist:
            return None

    def get(self, request, public_id):
        rep = self.get_object(public_id)

        if not rep:
            return Response(
                {"success": False, "message": "Tenant authorised representative not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantAuthorisedRepresentativeSerializer(rep)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantAuthorisedRepresentativeSerializer)
    def put(self, request, public_id):
        rep = self.get_object(public_id)

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

    def delete(self, request, public_id):
        rep = self.get_object(public_id)

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

    @extend_schema(request=TenantContactSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantContactSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantContact.objects.get(public_id=public_id)
        except TenantContact.DoesNotExist:
            return None

    def get(self, request, public_id):
        contact = self.get_object(public_id)

        if not contact:
            return Response(
                {"success": False, "message": "Tenant contact not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantContactSerializer(contact)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantContactSerializer)
    def put(self, request, public_id):
        contact = self.get_object(public_id)

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

    def delete(self, request, public_id):
        contact = self.get_object(public_id)

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
# No public_id (no UUIDModel) -> keyed by pk. No PUT/DELETE by design.
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

    @extend_schema(request=TenantVerificationSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantVerificationSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantVerification.objects.get(public_id=public_id)
        except TenantVerification.DoesNotExist:
            return None

    def get(self, request, public_id):
        verification = self.get_object(public_id)

        if not verification:
            return Response(
                {"success": False, "message": "Tenant verification not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantVerificationSerializer(verification)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantVerificationSerializer)
    def put(self, request, public_id):
        verification = self.get_object(public_id)

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

    def delete(self, request, public_id):
        verification = self.get_object(public_id)

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

    @extend_schema(request=TenantDocumentSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantDocumentSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantDocument.objects.get(public_id=public_id)
        except TenantDocument.DoesNotExist:
            return None

    def get(self, request, public_id):
        document = self.get_object(public_id)

        if not document:
            return Response(
                {"success": False, "message": "Tenant document not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantDocumentSerializer(document)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantDocumentSerializer)
    def put(self, request, public_id):
        document = self.get_object(public_id)

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

    def delete(self, request, public_id):
        document = self.get_object(public_id)

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

    @extend_schema(request=TenantLegalAcceptanceSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantLegalAcceptanceSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantLegalAcceptance.objects.get(public_id=public_id)
        except TenantLegalAcceptance.DoesNotExist:
            return None

    def get(self, request, public_id):
        acceptance = self.get_object(public_id)

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

    @extend_schema(request=TenantLegalSettingsSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantLegalSettingsSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantLegalSettings.objects.get(public_id=public_id)
        except TenantLegalSettings.DoesNotExist:
            return None

    def get(self, request, public_id):
        settings_obj = self.get_object(public_id)

        if not settings_obj:
            return Response(
                {"success": False, "message": "Tenant legal settings not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantLegalSettingsSerializer(settings_obj)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantLegalSettingsSerializer)
    def put(self, request, public_id):
        settings_obj = self.get_object(public_id)

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

    def delete(self, request, public_id):
        settings_obj = self.get_object(public_id)

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

    @extend_schema(request=TenantNdaSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantNdaSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantNda.objects.get(public_id=public_id)
        except TenantNda.DoesNotExist:
            return None

    def get(self, request, public_id):
        nda = self.get_object(public_id)

        if not nda:
            return Response(
                {"success": False, "message": "Tenant NDA not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantNdaSerializer(nda)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantNdaSerializer)
    def put(self, request, public_id):
        nda = self.get_object(public_id)

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

    def delete(self, request, public_id):
        nda = self.get_object(public_id)

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

    @extend_schema(request=TenantSettingsSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantSettingsSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantSettings.objects.get(public_id=public_id)
        except TenantSettings.DoesNotExist:
            return None

    def get(self, request, public_id):
        settings_obj = self.get_object(public_id)

        if not settings_obj:
            return Response(
                {"success": False, "message": "Tenant settings not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantSettingsSerializer(settings_obj)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantSettingsSerializer)
    def put(self, request, public_id):
        settings_obj = self.get_object(public_id)

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

    def delete(self, request, public_id):
        settings_obj = self.get_object(public_id)

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

    @extend_schema(request=TenantSubscriptionSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantSubscriptionSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantSubscription.objects.get(public_id=public_id)
        except TenantSubscription.DoesNotExist:
            return None

    def get(self, request, public_id):
        subscription = self.get_object(public_id)

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

    @extend_schema(request=ModuleSerializer)
    def post(self, request):
        serializer = ModuleSerializer(data=request.data)

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

    def get_object(self, public_id):
        try:
            return Module.objects.get(public_id=public_id)
        except Module.DoesNotExist:
            return None

    def get(self, request, public_id):
        module = self.get_object(public_id)

        if not module:
            return Response(
                {"success": False, "message": "Module not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ModuleSerializer(module)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=ModuleSerializer)
    def put(self, request, public_id):
        module = self.get_object(public_id)

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

    def delete(self, request, public_id):
        module = self.get_object(public_id)

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

    @extend_schema(request=TenantModuleEntitlementSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantModuleEntitlementSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantModuleEntitlement.objects.get(public_id=public_id)
        except TenantModuleEntitlement.DoesNotExist:
            return None

    def get(self, request, public_id):
        entitlement = self.get_object(public_id)

        if not entitlement:
            return Response(
                {"success": False, "message": "Tenant module entitlement not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantModuleEntitlementSerializer(entitlement)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantModuleEntitlementSerializer)
    def put(self, request, public_id):
        entitlement = self.get_object(public_id)

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

    def delete(self, request, public_id):
        entitlement = self.get_object(public_id)

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

    @extend_schema(request=TenantBrandingSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantBrandingSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantBranding.objects.get(public_id=public_id)
        except TenantBranding.DoesNotExist:
            return None

    def get(self, request, public_id):
        branding = self.get_object(public_id)

        if not branding:
            return Response(
                {"success": False, "message": "Tenant branding not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantBrandingSerializer(branding)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantBrandingSerializer)
    def put(self, request, public_id):
        branding = self.get_object(public_id)

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

    def delete(self, request, public_id):
        branding = self.get_object(public_id)

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

    @extend_schema(request=TenantReportTemplateSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantReportTemplateSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantReportTemplate.objects.get(public_id=public_id)
        except TenantReportTemplate.DoesNotExist:
            return None

    def get(self, request, public_id):
        template = self.get_object(public_id)

        if not template:
            return Response(
                {"success": False, "message": "Tenant report template not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantReportTemplateSerializer(template)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantReportTemplateSerializer)
    def put(self, request, public_id):
        template = self.get_object(public_id)

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

    def delete(self, request, public_id):
        template = self.get_object(public_id)

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

    @extend_schema(request=TenantSecuritySettingsSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantSecuritySettingsSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantSecuritySettings.objects.get(public_id=public_id)
        except TenantSecuritySettings.DoesNotExist:
            return None

    def get(self, request, public_id):
        settings_obj = self.get_object(public_id)

        if not settings_obj:
            return Response(
                {"success": False, "message": "Tenant security settings not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantSecuritySettingsSerializer(settings_obj)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantSecuritySettingsSerializer)
    def put(self, request, public_id):
        settings_obj = self.get_object(public_id)

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

    def delete(self, request, public_id):
        settings_obj = self.get_object(public_id)

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

    @extend_schema(request=TenantIPRestrictionSerializer)
    def post(self, request):
        serializer = TenantIPRestrictionSerializer(data=request.data)

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

    def get_object(self, public_id):
        try:
            return TenantIPRestriction.objects.get(public_id=public_id)
        except TenantIPRestriction.DoesNotExist:
            return None

    def get(self, request, public_id):
        restriction = self.get_object(public_id)

        if not restriction:
            return Response(
                {"success": False, "message": "Tenant IP restriction not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantIPRestrictionSerializer(restriction)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantIPRestrictionSerializer)
    def put(self, request, public_id):
        restriction = self.get_object(public_id)

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

    def delete(self, request, public_id):
        restriction = self.get_object(public_id)

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

    @extend_schema(request=TenantIntegrationSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantIntegrationSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantIntegration.objects.get(public_id=public_id)
        except TenantIntegration.DoesNotExist:
            return None

    def get(self, request, public_id):
        integration = self.get_object(public_id)

        if not integration:
            return Response(
                {"success": False, "message": "Tenant integration not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantIntegrationSerializer(integration)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantIntegrationSerializer)
    def put(self, request, public_id):
        integration = self.get_object(public_id)

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

    def delete(self, request, public_id):
        integration = self.get_object(public_id)

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

    @extend_schema(request=TenantBillingSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantBillingSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantBilling.objects.get(public_id=public_id)
        except TenantBilling.DoesNotExist:
            return None

    def get(self, request, public_id):
        billing = self.get_object(public_id)

        if not billing:
            return Response(
                {"success": False, "message": "Tenant billing not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantBillingSerializer(billing)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantBillingSerializer)
    def put(self, request, public_id):
        billing = self.get_object(public_id)

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

    def delete(self, request, public_id):
        billing = self.get_object(public_id)

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

    @extend_schema(request=TenantInvitationSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantInvitationSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantInvitation.objects.get(public_id=public_id)
        except TenantInvitation.DoesNotExist:
            return None

    def get(self, request, public_id):
        invitation = self.get_object(public_id)

        if not invitation:
            return Response(
                {"success": False, "message": "Tenant invitation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantInvitationSerializer(invitation)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantInvitationSerializer)
    def put(self, request, public_id):
        invitation = self.get_object(public_id)

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

    def delete(self, request, public_id):
        invitation = self.get_object(public_id)

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

    @extend_schema(request=TenantWorkflowSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantWorkflowSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantWorkflow.objects.get(public_id=public_id)
        except TenantWorkflow.DoesNotExist:
            return None

    def get(self, request, public_id):
        workflow = self.get_object(public_id)

        if not workflow:
            return Response(
                {"success": False, "message": "Tenant workflow not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantWorkflowSerializer(workflow)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantWorkflowSerializer)
    def put(self, request, public_id):
        workflow = self.get_object(public_id)

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

    def delete(self, request, public_id):
        workflow = self.get_object(public_id)

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

    @extend_schema(request=TenantWorkflowStepSerializer)
    def post(self, request):
        serializer = TenantWorkflowStepSerializer(data=request.data)

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

    def get_object(self, public_id):
        try:
            return TenantWorkflowStep.objects.get(public_id=public_id)
        except TenantWorkflowStep.DoesNotExist:
            return None

    def get(self, request, public_id):
        step = self.get_object(public_id)

        if not step:
            return Response(
                {"success": False, "message": "Tenant workflow step not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantWorkflowStepSerializer(step)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantWorkflowStepSerializer)
    def put(self, request, public_id):
        step = self.get_object(public_id)

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

    def delete(self, request, public_id):
        step = self.get_object(public_id)

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

    @extend_schema(request=TenantOperationLogSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantOperationLogSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantOperationLog.objects.get(public_id=public_id)
        except TenantOperationLog.DoesNotExist:
            return None

    def get(self, request, public_id):
        log = self.get_object(public_id)

        if not log:
            return Response(
                {"success": False, "message": "Tenant operation log not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantOperationLogSerializer(log)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantOperationLogSerializer)
    def put(self, request, public_id):
        log = self.get_object(public_id)

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

    def delete(self, request, public_id):
        log = self.get_object(public_id)

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

    @extend_schema(request=TenantTerminologySerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantTerminologySerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantTerminology.objects.get(public_id=public_id)
        except TenantTerminology.DoesNotExist:
            return None

    def get(self, request, public_id):
        term = self.get_object(public_id)

        if not term:
            return Response(
                {"success": False, "message": "Tenant terminology not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantTerminologySerializer(term)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantTerminologySerializer)
    def put(self, request, public_id):
        term = self.get_object(public_id)

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

    def delete(self, request, public_id):
        term = self.get_object(public_id)

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

    @extend_schema(request=TenantNumberingConfigSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantNumberingConfigSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantNumberingConfig.objects.get(public_id=public_id)
        except TenantNumberingConfig.DoesNotExist:
            return None

    def get(self, request, public_id):
        config = self.get_object(public_id)

        if not config:
            return Response(
                {"success": False, "message": "Tenant numbering config not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantNumberingConfigSerializer(config)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantNumberingConfigSerializer)
    def put(self, request, public_id):
        config = self.get_object(public_id)

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

    def delete(self, request, public_id):
        config = self.get_object(public_id)

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

    @extend_schema(request=TenantApprovalMatrixSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantApprovalMatrixSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantApprovalMatrix.objects.get(public_id=public_id)
        except TenantApprovalMatrix.DoesNotExist:
            return None

    def get(self, request, public_id):
        matrix = self.get_object(public_id)

        if not matrix:
            return Response(
                {"success": False, "message": "Tenant approval matrix not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantApprovalMatrixSerializer(matrix)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantApprovalMatrixSerializer)
    def put(self, request, public_id):
        matrix = self.get_object(public_id)

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

    def delete(self, request, public_id):
        matrix = self.get_object(public_id)

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

    @extend_schema(request=TenantNotificationSettingsSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = TenantNotificationSettingsSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return TenantNotificationSettings.objects.get(public_id=public_id)
        except TenantNotificationSettings.DoesNotExist:
            return None

    def get(self, request, public_id):
        settings_obj = self.get_object(public_id)

        if not settings_obj:
            return Response(
                {"success": False, "message": "Tenant notification settings not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TenantNotificationSettingsSerializer(settings_obj)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=TenantNotificationSettingsSerializer)
    def put(self, request, public_id):
        settings_obj = self.get_object(public_id)

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

    def delete(self, request, public_id):
        settings_obj = self.get_object(public_id)

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

    @extend_schema(request=ConflictOfInterestDeclarationSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = ConflictOfInterestDeclarationSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return ConflictOfInterestDeclaration.objects.get(public_id=public_id)
        except ConflictOfInterestDeclaration.DoesNotExist:
            return None

    def get(self, request, public_id):
        declaration = self.get_object(public_id)

        if not declaration:
            return Response(
                {"success": False, "message": "Conflict of interest declaration not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ConflictOfInterestDeclarationSerializer(declaration)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=ConflictOfInterestDeclarationSerializer)
    def put(self, request, public_id):
        declaration = self.get_object(public_id)

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

    def delete(self, request, public_id):
        declaration = self.get_object(public_id)

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

    @extend_schema(request=DataExportRequestSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = DataExportRequestSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return DataExportRequest.objects.get(public_id=public_id)
        except DataExportRequest.DoesNotExist:
            return None

    def get(self, request, public_id):
        export_request = self.get_object(public_id)

        if not export_request:
            return Response(
                {"success": False, "message": "Data export request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DataExportRequestSerializer(export_request)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=DataExportRequestSerializer)
    def put(self, request, public_id):
        export_request = self.get_object(public_id)

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

    def delete(self, request, public_id):
        export_request = self.get_object(public_id)

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

    @extend_schema(request=ProjectSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = ProjectSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return Project.objects.get(public_id=public_id)
        except Project.DoesNotExist:
            return None

    def get(self, request, public_id):
        project = self.get_object(public_id)

        if not project:
            return Response(
                {"success": False, "message": "Project not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectSerializer(project)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=ProjectSerializer)
    def put(self, request, public_id):
        project = self.get_object(public_id)

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

    def delete(self, request, public_id):
        project = self.get_object(public_id)

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

    @extend_schema(request=ProjectRequirementSerializer)
    def post(self, request):
        serializer = ProjectRequirementSerializer(data=request.data)

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

    def get_object(self, public_id):
        try:
            return ProjectRequirement.objects.get(public_id=public_id)
        except ProjectRequirement.DoesNotExist:
            return None

    def get(self, request, public_id):
        requirement = self.get_object(public_id)

        if not requirement:
            return Response(
                {"success": False, "message": "Project requirement not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectRequirementSerializer(requirement)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=ProjectRequirementSerializer)
    def put(self, request, public_id):
        requirement = self.get_object(public_id)

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

    def delete(self, request, public_id):
        requirement = self.get_object(public_id)

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

    @extend_schema(request=ProjectRequirementScopeSerializer)
    def post(self, request):
        serializer = ProjectRequirementScopeSerializer(data=request.data)

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

    def get_object(self, public_id):
        try:
            return ProjectRequirementScope.objects.get(public_id=public_id)
        except ProjectRequirementScope.DoesNotExist:
            return None

    def get(self, request, public_id):
        scope = self.get_object(public_id)

        if not scope:
            return Response(
                {"success": False, "message": "Project requirement scope not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectRequirementScopeSerializer(scope)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=ProjectRequirementScopeSerializer)
    def put(self, request, public_id):
        scope = self.get_object(public_id)

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

    def delete(self, request, public_id):
        scope = self.get_object(public_id)

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

    @extend_schema(request=ProjectCandidateSerializer)
    def post(self, request):
        serializer = ProjectCandidateSerializer(data=request.data)

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

    def get_object(self, public_id):
        try:
            return ProjectCandidate.objects.get(public_id=public_id)
        except ProjectCandidate.DoesNotExist:
            return None

    def get(self, request, public_id):
        candidate = self.get_object(public_id)

        if not candidate:
            return Response(
                {"success": False, "message": "Project candidate not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectCandidateSerializer(candidate)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=ProjectCandidateSerializer)
    def put(self, request, public_id):
        candidate = self.get_object(public_id)

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

    def delete(self, request, public_id):
        candidate = self.get_object(public_id)

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

    @extend_schema(request=DisclosureRequestSerializer)
    def post(self, request):
        data = request.data.copy()
        data["tenant"] = resolve_tenant(request)

        serializer = DisclosureRequestSerializer(data=data)

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

    def get_object(self, public_id):
        try:
            return DisclosureRequest.objects.get(public_id=public_id)
        except DisclosureRequest.DoesNotExist:
            return None

    def get(self, request, public_id):
        disclosure = self.get_object(public_id)

        if not disclosure:
            return Response(
                {"success": False, "message": "Disclosure request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DisclosureRequestSerializer(disclosure)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=DisclosureRequestSerializer)
    def put(self, request, public_id):
        disclosure = self.get_object(public_id)

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

    def delete(self, request, public_id):
        disclosure = self.get_object(public_id)

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

    @extend_schema(request=CandidateConsentSerializer)
    def post(self, request):
        serializer = CandidateConsentSerializer(data=request.data)

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

    def get_object(self, public_id):
        try:
            return CandidateConsent.objects.get(public_id=public_id)
        except CandidateConsent.DoesNotExist:
            return None

    def get(self, request, public_id):
        consent = self.get_object(public_id)

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

    @extend_schema(request=ProjectPlacementSerializer)
    def post(self, request):
        serializer = ProjectPlacementSerializer(data=request.data)

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

    def get_object(self, public_id):
        try:
            return ProjectPlacement.objects.get(public_id=public_id)
        except ProjectPlacement.DoesNotExist:
            return None

    def get(self, request, public_id):
        placement = self.get_object(public_id)

        if not placement:
            return Response(
                {"success": False, "message": "Project placement not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectPlacementSerializer(placement)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=ProjectPlacementSerializer)
    def put(self, request, public_id):
        placement = self.get_object(public_id)

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

    def delete(self, request, public_id):
        placement = self.get_object(public_id)

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

    @extend_schema(request=ProjectScopeLinkSerializer)
    def post(self, request):
        serializer = ProjectScopeLinkSerializer(data=request.data)

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

    def get_object(self, public_id):
        try:
            return ProjectScopeLink.objects.get(public_id=public_id)
        except ProjectScopeLink.DoesNotExist:
            return None

    def get(self, request, public_id):
        link = self.get_object(public_id)

        if not link:
            return Response(
                {"success": False, "message": "Project scope link not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectScopeLinkSerializer(link)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=ProjectScopeLinkSerializer)
    def put(self, request, public_id):
        link = self.get_object(public_id)

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

    def delete(self, request, public_id):
        link = self.get_object(public_id)

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






