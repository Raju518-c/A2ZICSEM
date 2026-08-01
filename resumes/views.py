from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .serializers import *

@method_decorator(csrf_exempt, name='dispatch')
class ResumeTemplateListCreateAPIView(APIView):
    """
    GET  : Get all resume templates
    POST : Create a new resume template
    """

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