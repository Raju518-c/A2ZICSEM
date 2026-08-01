from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    CapabilityRecord,
    ContactRecord,
    CredentialRecord,
    ProfessionalProfile,
    ProfessionalReview,
)
from .serializers import (
    CapabilityRecordSerializer,
    ContactRecordSerializer,
    CredentialRecordSerializer,
    ProfessionalProfileSerializer,
    ProfessionalReviewSerializer,
)

@method_decorator(csrf_exempt, name='dispatch')
class ProfessionalProfileListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        profiles = ProfessionalProfile.objects.all().order_by("-created_at")
        serializer = ProfessionalProfileSerializer(profiles, many=True)
        return Response(
            {"success": True, "message": "Professional profiles fetched successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=ProfessionalProfileSerializer)
    def post(self, request):
        serializer = ProfessionalProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Professional profile created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class ProfessionalProfileRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return ProfessionalProfile.objects.get(pk=pk)
        except ProfessionalProfile.DoesNotExist:
            return None

    def get(self, request, pk):
        profile = self.get_object(pk)
        if not profile:
            return Response({"success": False, "message": "Professional profile not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfessionalProfileSerializer(profile)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
    @extend_schema(request=ProfessionalProfileSerializer)
    def put(self, request, pk):
        profile = self.get_object(pk)
        if not profile:
            return Response({"success": False, "message": "Professional profile not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfessionalProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Professional profile updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        profile = self.get_object(pk)
        if not profile:
            return Response({"success": False, "message": "Professional profile not found."}, status=status.HTTP_404_NOT_FOUND)
        profile.delete()
        return Response({"success": True, "message": "Professional profile deleted successfully."}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class ProfessionalReviewListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        reviews = ProfessionalReview.objects.all().order_by("-created_at")
        serializer = ProfessionalReviewSerializer(reviews, many=True)
        return Response(
            {"success": True, "message": "Professional reviews fetched successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=ProfessionalReviewSerializer)
    def post(self, request):
        serializer = ProfessionalReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Professional review created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class ProfessionalReviewRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return ProfessionalReview.objects.get(pk=pk)
        except ProfessionalReview.DoesNotExist:
            return None

    def get(self, request, pk):
        review = self.get_object(pk)
        if not review:
            return Response({"success": False, "message": "Professional review not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfessionalReviewSerializer(review)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
    @extend_schema(request=ProfessionalReviewSerializer)
    def put(self, request, pk):
        review = self.get_object(pk)
        if not review:
            return Response({"success": False, "message": "Professional review not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfessionalReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Professional review updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        review = self.get_object(pk)
        if not review:
            return Response({"success": False, "message": "Professional review not found."}, status=status.HTTP_404_NOT_FOUND)
        review.delete()
        return Response({"success": True, "message": "Professional review deleted successfully."}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class CredentialRecordListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        credentials = CredentialRecord.objects.all().order_by("-created_at")
        serializer = CredentialRecordSerializer(credentials, many=True)
        return Response(
            {"success": True, "message": "Credential records fetched successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=CredentialRecordSerializer)
    def post(self, request):
        serializer = CredentialRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Credential record created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class CredentialRecordRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return CredentialRecord.objects.get(pk=pk)
        except CredentialRecord.DoesNotExist:
            return None

    def get(self, request, pk):
        credential = self.get_object(pk)
        if not credential:
            return Response({"success": False, "message": "Credential record not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CredentialRecordSerializer(credential)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
    @extend_schema(request=CredentialRecordSerializer)
    def put(self, request, pk):
        credential = self.get_object(pk)
        if not credential:
            return Response({"success": False, "message": "Credential record not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CredentialRecordSerializer(credential, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Credential record updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        credential = self.get_object(pk)
        if not credential:
            return Response({"success": False, "message": "Credential record not found."}, status=status.HTTP_404_NOT_FOUND)
        credential.delete()
        return Response({"success": True, "message": "Credential record deleted successfully."}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class CapabilityRecordListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        capabilities = CapabilityRecord.objects.all().order_by("-created_at")
        serializer = CapabilityRecordSerializer(capabilities, many=True)
        return Response(
            {"success": True, "message": "Capability records fetched successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=CapabilityRecordSerializer)
    def post(self, request):
        serializer = CapabilityRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Capability record created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class CapabilityRecordRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return CapabilityRecord.objects.get(pk=pk)
        except CapabilityRecord.DoesNotExist:
            return None

    def get(self, request, pk):
        capability = self.get_object(pk)
        if not capability:
            return Response({"success": False, "message": "Capability record not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CapabilityRecordSerializer(capability)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
    @extend_schema(request=CapabilityRecordSerializer)
    def put(self, request, pk):
        capability = self.get_object(pk)
        if not capability:
            return Response({"success": False, "message": "Capability record not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CapabilityRecordSerializer(capability, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Capability record updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        capability = self.get_object(pk)
        if not capability:
            return Response({"success": False, "message": "Capability record not found."}, status=status.HTTP_404_NOT_FOUND)
        capability.delete()
        return Response({"success": True, "message": "Capability record deleted successfully."}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class ContactRecordListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        contacts = ContactRecord.objects.all().order_by("-created_at")
        serializer = ContactRecordSerializer(contacts, many=True)
        return Response(
            {"success": True, "message": "Contact records fetched successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=ContactRecordSerializer)
    def post(self, request):
        serializer = ContactRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Contact record created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class ContactRecordRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return ContactRecord.objects.get(pk=pk)
        except ContactRecord.DoesNotExist:
            return None

    def get(self, request, pk):
        contact = self.get_object(pk)
        if not contact:
            return Response({"success": False, "message": "Contact record not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ContactRecordSerializer(contact)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
    @extend_schema(request=ContactRecordSerializer)
    def put(self, request, pk):
        contact = self.get_object(pk)
        if not contact:
            return Response({"success": False, "message": "Contact record not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ContactRecordSerializer(contact, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Contact record updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        contact = self.get_object(pk)
        if not contact:
            return Response({"success": False, "message": "Contact record not found."}, status=status.HTTP_404_NOT_FOUND)
        contact.delete()
        return Response({"success": True, "message": "Contact record deleted successfully."}, status=status.HTTP_200_OK)
