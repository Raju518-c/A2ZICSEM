from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
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

    @extend_schema(request=TenantSerializer)
    def post(self, request):
        tenant_payload = request.data.get("tenant", request.data or {})
        operations_payload = request.data.get("operations", [])
        role_payload = request.data.get("role", {})
        user_payload = request.data.get("user", {})

        if not isinstance(tenant_payload, dict):
            return Response(
                {"success": False, "errors": {"tenant": ["Tenant payload must be an object."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(operations_payload, list):
            operations_payload = [operations_payload] if operations_payload else []

        if not isinstance(role_payload, dict):
            role_payload = {"code": str(role_payload)} if role_payload else {}

        if not isinstance(user_payload, dict):
            return Response(
                {"success": False, "errors": {"user": ["User payload must be an object."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not tenant_payload.get("name") or not tenant_payload.get("code") or not tenant_payload.get("portal_slug"):
            return Response(
                {
                    "success": False,
                    "errors": {
                        "tenant": ["name, code and portal_slug are required."]
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_email = (user_payload.get("email") or "").strip().lower()
        user_mobile_country_code = user_payload.get("mobile_country_code")
        user_mobile_number = user_payload.get("mobile_number")
        password = user_payload.get("password")

        if not user_email or not user_mobile_country_code or not user_mobile_number or not password:
            return Response(
                {
                    "success": False,
                    "errors": {
                        "user": ["email, mobile_country_code, mobile_number and password are required."]
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                admin_user = UserTbl.objects.create(
                    email=user_email,
                    mobile_country_code=user_mobile_country_code,
                    mobile_number=user_mobile_number,
                    password=password,
                    approval_status=user_payload.get(
                        "approval_status", UserTbl.ApprovalStatus.APPROVED
                    ),
                    is_active=user_payload.get("is_active", True),
                    is_staff=user_payload.get("is_staff", True),
                    is_superuser=user_payload.get("is_superuser", False),
                )

                tenant_data = dict(tenant_payload)
                tenant_data["created_by"] = admin_user.pk

                tenant_serializer = TenantSerializer(data=tenant_data)
                if not tenant_serializer.is_valid():
                    return Response(
                        {"success": False, "errors": tenant_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                tenant = tenant_serializer.save()
                admin_user.tenant = tenant
                admin_user.save(update_fields=["tenant", "updated_at"])

                role_code = role_payload.get("code") or user_payload.get("role") or "Admin"
                role_name = role_payload.get("name") or role_code or "Admin"
                role_for = (
                    role_payload.get("roles_for")
                    or user_payload.get("roles_for")
                    or "tenant admin"
                )

                role_obj, _ = roles.objects.get_or_create(
                    code=role_code,
                    tenant=tenant,
                    defaults={"name": role_name, "roles_for": role_for},
                )
                admin_user.role.add(role_obj)

                created_operations = []
                for operation_payload in operations_payload:
                    if not isinstance(operation_payload, dict):
                        continue

                    operation_data = {
                        "tenant": tenant.pk,
                        "industry": operation_payload.get("industry")
                        or operation_payload.get("industry_id"),
                        "country_code": operation_payload.get("country_code"),
                        "region_name": operation_payload.get("region_name", ""),
                        "is_registration_enabled": operation_payload.get(
                            "is_registration_enabled", True
                        ),
                        "is_active": operation_payload.get("is_active", True),
                        "effective_from": operation_payload.get("effective_from"),
                        "effective_to": operation_payload.get("effective_to"),
                        "created_by": admin_user.pk,
                    }

                    operation_serializer = TenantOperationSerializer(data=operation_data)
                    if not operation_serializer.is_valid():
                        return Response(
                            {"success": False, "errors": operation_serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    created_operations.append(operation_serializer.save())

                return Response(
                    {
                        "success": True,
                        "message": "Tenant, operations, role and admin user created successfully.",
                        "data": {
                            "tenant": TenantSerializer(tenant).data,
                            "operations": TenantOperationSerializer(
                                created_operations, many=True
                            ).data,
                            "role": {
                                "code": role_obj.code,
                                "name": role_obj.name,
                                "roles_for": role_obj.roles_for,
                            },
                            "user": {
                                "id": str(admin_user.public_id),
                                "email": admin_user.email,
                                "tenant_id": tenant.pk,
                            },
                        },
                    },
                    status=status.HTTP_201_CREATED,
                )
        except Exception as exc:
            return Response(
                {"success": False, "errors": {"detail": str(exc)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
            

@method_decorator(csrf_exempt, name='dispatch')
class TenantListCreateAPIView(APIView):
    """
    GET  : Get all tenants
    POST : Create a new tenant
    """

    permission_classes = [AllowAny]

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
    
    @extend_schema(request=TenantSerializer)
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
    
    @extend_schema(request=TenantSerializer)
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
        

