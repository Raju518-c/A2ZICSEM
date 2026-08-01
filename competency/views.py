from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .serializers import *


class ProfessionalScopeListCreateAPIView(APIView):
    """
    GET  : Get all professional scopes
    POST : Create a new professional scope
    """

    def get(self, request):
        professional_scopes = ProfessionalScope.objects.all().order_by(
            "professional",
            "scope"
        )

        serializer = ProfessionalScopeSerializer(
            professional_scopes,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": "Professional scopes fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ProfessionalScopeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Professional scope created successfully.",
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




class ProfessionalScopeRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Retrieve professional scope by ID
    PUT    : Update professional scope
    DELETE : Delete professional scope
    """

    def get_object(self, pk):
        try:
            return ProfessionalScope.objects.get(pk=pk)
        except ProfessionalScope.DoesNotExist:
            return None

    def get(self, request, pk):
        professional_scope = self.get_object(pk)

        if not professional_scope:
            return Response(
                {
                    "success": False,
                    "message": "Professional scope not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProfessionalScopeSerializer(professional_scope)

        return Response(
            {
                "success": True,
                "message": "Professional scope retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        professional_scope = self.get_object(pk)

        if not professional_scope:
            return Response(
                {
                    "success": False,
                    "message": "Professional scope not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProfessionalScopeSerializer(
            professional_scope,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Professional scope updated successfully.",
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
        professional_scope = self.get_object(pk)

        if not professional_scope:
            return Response(
                {
                    "success": False,
                    "message": "Professional scope not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        professional_scope.delete()

        return Response(
            {
                "success": True,
                "message": "Professional scope deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )





class CompetencyAssessmentListCreateAPIView(APIView):
    """
    GET  : Get all competency assessments
    POST : Create a new competency assessment
    """

    def get(self, request):
        competency_assessments = CompetencyAssessment.objects.all().order_by("-created_at")

        serializer = CompetencyAssessmentSerializer(
            competency_assessments,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": "Competency assessments fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = CompetencyAssessmentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Competency assessment created successfully.",
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



class CompetencyAssessmentRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Retrieve competency assessment by ID
    PUT    : Update competency assessment
    DELETE : Delete competency assessment
    """

    def get_object(self, pk):
        try:
            return CompetencyAssessment.objects.get(pk=pk)
        except CompetencyAssessment.DoesNotExist:
            return None

    def get(self, request, pk):
        competency_assessment = self.get_object(pk)

        if not competency_assessment:
            return Response(
                {
                    "success": False,
                    "message": "Competency assessment not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CompetencyAssessmentSerializer(competency_assessment)

        return Response(
            {
                "success": True,
                "message": "Competency assessment retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        competency_assessment = self.get_object(pk)

        if not competency_assessment:
            return Response(
                {
                    "success": False,
                    "message": "Competency assessment not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CompetencyAssessmentSerializer(
            competency_assessment,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Competency assessment updated successfully.",
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
        competency_assessment = self.get_object(pk)

        if not competency_assessment:
            return Response(
                {
                    "success": False,
                    "message": "Competency assessment not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        competency_assessment.delete()

        return Response(
            {
                "success": True,
                "message": "Competency assessment deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )