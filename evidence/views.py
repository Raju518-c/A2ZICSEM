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
class EvidenceDocumentListCreateAPIView(APIView):
    """
    GET  : Get all evidence documents
    POST : Create a new evidence document
    """

    def get(self, request):
        evidence_documents = EvidenceDocument.objects.all().order_by("-uploaded_at")

        serializer = EvidenceDocumentSerializer(
            evidence_documents,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": "Evidence documents fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=EvidenceDocumentSerializer)
    def post(self, request):
        serializer = EvidenceDocumentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Evidence document created successfully.",
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
class EvidenceDocumentRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Retrieve evidence document by ID
    PUT    : Update evidence document
    DELETE : Delete evidence document
    """

    def get_object(self, pk):
        try:
            return EvidenceDocument.objects.get(pk=pk)
        except EvidenceDocument.DoesNotExist:
            return None

    def get(self, request, pk):
        evidence = self.get_object(pk)

        if not evidence:
            return Response(
                {
                    "success": False,
                    "message": "Evidence document not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EvidenceDocumentSerializer(evidence)

        return Response(
            {
                "success": True,
                "message": "Evidence document retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=EvidenceDocumentSerializer)
    def put(self, request, pk):
        evidence = self.get_object(pk)

        if not evidence:
            return Response(
                {
                    "success": False,
                    "message": "Evidence document not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EvidenceDocumentSerializer(
            evidence,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Evidence document updated successfully.",
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
        evidence = self.get_object(pk)

        if not evidence:
            return Response(
                {
                    "success": False,
                    "message": "Evidence document not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        evidence.delete()

        return Response(
            {
                "success": True,
                "message": "Evidence document deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )