from django.db import IntegrityError, transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .models import EcosystemMember
from .serializers import EcosystemMemberSerializer


class EcosystemMemberListCreateAPIView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):
        try:
            members = EcosystemMember.objects.all().order_by("-joined_at")

            serializer = EcosystemMemberSerializer(
                members,
                many=True
            )

            return Response({
                "success": True,
                "message": "Ecosystem members fetched successfully.",
                "count": members.count(),
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception:
            return Response({
                "success": False,
                "message": "Unable to fetch ecosystem members."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = EcosystemMemberSerializer(
                data=request.data
            )

            if not serializer.is_valid():
                return Response({
                    "success": False,
                    "message": "Validation failed.",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                serializer.save()

            return Response({
                "success": True,
                "message": "Successfully joined the Qualion ecosystem.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({
                "success": False,
                "message": "This email is already registered in Join Ecosystem."
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            return Response({
                "success": False,
                "message": "Unable to submit your interest."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EcosystemMemberDetailAPIView(APIView):

    # Replace with appropriate admin permissions before production.
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            member = EcosystemMember.objects.get(pk=pk)

            serializer = EcosystemMemberSerializer(member)

            return Response({
                "success": True,
                "message": "Ecosystem member fetched successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except EcosystemMember.DoesNotExist:
            return Response({
                "success": False,
                "message": "Ecosystem member not found."
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception:
            return Response({
                "success": False,
                "message": "Unable to fetch ecosystem member."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            member = EcosystemMember.objects.get(pk=pk)

            serializer = EcosystemMemberSerializer(
                member,
                data=request.data,
                partial=True
            )

            if not serializer.is_valid():
                return Response({
                    "success": False,
                    "message": "Validation failed.",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                serializer.save()

            return Response({
                "success": True,
                "message": "Ecosystem member updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except EcosystemMember.DoesNotExist:
            return Response({
                "success": False,
                "message": "Ecosystem member not found."
            }, status=status.HTTP_404_NOT_FOUND)

        except IntegrityError:
            return Response({
                "success": False,
                "message": "This email is already registered in Join Ecosystem."
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            return Response({
                "success": False,
                "message": "Unable to update ecosystem member."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            member = EcosystemMember.objects.get(pk=pk)

            member.delete()

            return Response({
                "success": True,
                "message": "Ecosystem member deleted successfully."
            }, status=status.HTTP_200_OK)

        except EcosystemMember.DoesNotExist:
            return Response({
                "success": False,
                "message": "Ecosystem member not found."
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception:
            return Response({
                "success": False,
                "message": "Unable to delete ecosystem member."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





