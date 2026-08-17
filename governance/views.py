from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import AuditEvent
from .serializers import AuditEventSerializer

@method_decorator(csrf_exempt, name='dispatch')
class AuditEventListCreateAPIView(APIView):
    """
    GET  : Get all audit events
    POST : Create a new audit event
    """
    permission_classes = [AllowAny]
   
    def get(self, request):
        audit_events = AuditEvent.objects.all().order_by("-occurred_at")

        serializer = AuditEventSerializer(
            audit_events,
            many=True,
        )

        return Response(
            {
                "success": True,
                "message": "Audit events fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=AuditEventSerializer)
    def post(self, request):
        serializer = AuditEventSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Audit event created successfully.",
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
class AuditEventRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Retrieve audit event by ID
    PUT    : Update audit event
    DELETE : Delete audit event
    """
    permission_classes = [AllowAny]
   
    def get_object(self, pk):
        try:
            return AuditEvent.objects.get(pk=pk)
        except AuditEvent.DoesNotExist:
            return None

    def get(self, request, pk):
        audit_event = self.get_object(pk)

        if not audit_event:
            return Response(
                {
                    "success": False,
                    "message": "Audit event not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AuditEventSerializer(audit_event)

        return Response(
            {
                "success": True,
                "message": "Audit event retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=AuditEventSerializer)
    def put(self, request, pk):
        audit_event = self.get_object(pk)

        if not audit_event:
            return Response(
                {
                    "success": False,
                    "message": "Audit event not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AuditEventSerializer(
            audit_event,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Audit event updated successfully.",
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
        audit_event = self.get_object(pk)

        if not audit_event:
            return Response(
                {
                    "success": False,
                    "message": "Audit event not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        audit_event.delete()

        return Response(
            {
                "success": True,
                "message": "Audit event deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )