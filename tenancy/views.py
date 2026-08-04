from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import parsers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serializers import *

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
        payload = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        if not payload:
            payload = request.POST.copy() if hasattr(request.POST, "copy") else dict(request.POST)

        if request.FILES:
            payload = payload.copy() if hasattr(payload, "copy") else dict(payload)
            for key, value in request.FILES.items():
                payload[key] = value

        serializer = TenantCombinedCreateSerializer(
            data=payload,
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
        

