from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import *
from .serializers import *

from rest_framework.permissions import IsAuthenticated
from professionals.models import *
from .services import *


@method_decorator(csrf_exempt, name='dispatch')
class ResumeTemplateListCreateAPIView(APIView):
    """
    GET  : Get all resume templates
    POST : Create a new resume template
    """
    permission_classes = [AllowAny]
   
    def get(self, request):
        resume_templates = ResumeTemplate.objects.all().order_by(
            "template_code",
            "version"
        )

        serializer = ResumeTemplateSerializer(
            resume_templates,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": "Resume templates fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=ResumeTemplateSerializer)
    def post(self, request):
        serializer = ResumeTemplateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Resume template created successfully.",
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
class ResumeTemplateRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Retrieve resume template by ID
    PUT    : Update resume template
    DELETE : Delete resume template
    """
    permission_classes = [AllowAny]
   
    def get_object(self, pk):
        try:
            return ResumeTemplate.objects.get(pk=pk)
        except ResumeTemplate.DoesNotExist:
            return None

    def get(self, request, pk):
        resume_template = self.get_object(pk)

        if not resume_template:
            return Response(
                {
                    "success": False,
                    "message": "Resume template not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ResumeTemplateSerializer(resume_template)

        return Response(
            {
                "success": True,
                "message": "Resume template retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=ResumeTemplateSerializer)
    def put(self, request, pk):
        resume_template = self.get_object(pk)

        if not resume_template:
            return Response(
                {
                    "success": False,
                    "message": "Resume template not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ResumeTemplateSerializer(
            resume_template,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Resume template updated successfully.",
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
        resume_template = self.get_object(pk)

        if not resume_template:
            return Response(
                {
                    "success": False,
                    "message": "Resume template not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        resume_template.delete()

        return Response(
            {
                "success": True,
                "message": "Resume template deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name='dispatch')
class ResumeGenerationListCreateAPIView(APIView):
    """
    GET  : Get all resume generations
    POST : Create a new resume generation
    """
    permission_classes = [AllowAny]
   
    def get(self, request):
        resume_generations = ResumeGeneration.objects.all().order_by(
            "-generated_at"
        )

        serializer = ResumeGenerationSerializer(
            resume_generations,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": "Resume generations fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=ResumeGenerationSerializer)
    def post(self, request):
        serializer = ResumeGenerationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Resume generation created successfully.",
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
class ResumeGenerationRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Retrieve resume generation by ID
    PUT    : Update resume generation
    DELETE : Delete resume generation
    """
    permission_classes = [AllowAny]
   
    def get_object(self, pk):
        try:
            return ResumeGeneration.objects.get(pk=pk)
        except ResumeGeneration.DoesNotExist:
            return None

    def get(self, request, pk):
        resume_generation = self.get_object(pk)

        if not resume_generation:
            return Response(
                {
                    "success": False,
                    "message": "Resume generation not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ResumeGenerationSerializer(resume_generation)

        return Response(
            {
                "success": True,
                "message": "Resume generation retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=ResumeGenerationSerializer)
    def put(self, request, pk):
        resume_generation = self.get_object(pk)

        if not resume_generation:
            return Response(
                {
                    "success": False,
                    "message": "Resume generation not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ResumeGenerationSerializer(
            resume_generation,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Resume generation updated successfully.",
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
        resume_generation = self.get_object(pk)

        if not resume_generation:
            return Response(
                {
                    "success": False,
                    "message": "Resume generation not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        resume_generation.delete()

        return Response(
            {
                "success": True,
                "message": "Resume generation deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )



class ResumeBuilderAPIView(APIView):
    """
    GET Resume Builder API.

    professional_profile_id is the integer
    primary key of ProfessionalProfile.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Build Resume",
        description=(
            "Build a dynamic resume using the "
            "ProfessionalProfile integer primary key."
        ),
        parameters=[

            OpenApiParameter(
                name="client_organization_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Client organization ID."
                ),
            ),

            OpenApiParameter(
                name="template_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "ResumeTemplate primary key."
                ),
            ),

            OpenApiParameter(
                name="scope_ids",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Comma-separated ScopeCatalog IDs. "
                    "Example: 1,2,3"
                ),
            ),
        ],

        responses={
            200: ResumeBuilderSerializer
        },
    )
    def get(
        self,
        request,
        professional_profile_id,
    ):

        # =====================================================
        # PROFESSIONAL PROFILE
        # =====================================================

        try:

            professional = (
                ProfessionalProfile.objects
                .select_related(
                    "user",
                    "primary_role",
                    "primary_industry",
                    "primary_scope",
                    "profile_photo_evidence",
                )
                .get(
                    id=professional_profile_id
                )
            )

        except ProfessionalProfile.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": (
                        "Professional profile "
                        "not found."
                    ),
                    "data": None,
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        # =====================================================
        # TENANT SECURITY
        # =====================================================

        request_tenant_id = getattr(
            request.user,
            "tenant_id",
            None,
        )

        professional_tenant_id = getattr(
            professional,
            "tenant_id",
            None,
        )

        if (
            request_tenant_id is not None
            and professional_tenant_id is not None
            and str(request_tenant_id)
            != str(professional_tenant_id)
        ):

            return Response(
                {
                    "success": False,
                    "message": (
                        "You do not have access "
                        "to this professional profile."
                    ),
                    "data": None,
                },
                status=(
                    status.HTTP_403_FORBIDDEN
                ),
            )

        # =====================================================
        # QUERY PARAMETERS
        # =====================================================

        client_organization_id = (
            request.query_params.get(
                "client_organization_id"
            )
        )

        template_id = (
            request.query_params.get(
                "template_id"
            )
        )

        scope_ids_param = (
            request.query_params.get(
                "scope_ids"
            )
        )

        # =====================================================
        # SCOPE IDS
        # =====================================================

        scope_ids = []

        if scope_ids_param:

            scope_ids = [
                value.strip()
                for value
                in scope_ids_param.split(",")
                if value.strip()
            ]

        # =====================================================
        # BUILD
        # =====================================================

        service = ResumeBuilderService(
            professional=professional,
            request=request,
            client_organization_id=(
                client_organization_id
            ),
            template_id=template_id,
            scope_ids=scope_ids,
        )

        try:

            data = service.build()

        except Exception as exc:

            return Response(
                {
                    "success": False,
                    "message": (
                        "Unable to build resume."
                    ),
                    "error": str(exc),
                },
                status=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )

        # =====================================================
        # SERIALIZER
        # =====================================================

        serializer = ResumeBuilderSerializer(
            data=data
        )

        serializer.is_valid(
            raise_exception=True
        )

        # =====================================================
        # RESPONSE
        # =====================================================

        return Response(
            {
                "success": True,
                "message": (
                    "Resume built successfully."
                ),
                "data": (
                    serializer.validated_data
                ),
            },
            status=status.HTTP_200_OK,
        )