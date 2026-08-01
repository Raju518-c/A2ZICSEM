from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import EmploymentRecord
from .serializers import EmploymentRecordSerializer


class EmploymentRecordListCreateAPIView(APIView):
    """
    GET  : Get all employment records
    POST : Create a new employment record
    """

    def get(self, request):
        employment_records = EmploymentRecord.objects.all().order_by("-start_date")

        serializer = EmploymentRecordSerializer(
            employment_records,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": "Employment records fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = EmploymentRecordSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Employment record created successfully.",
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





class EmploymentRecordRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Retrieve employment record by ID
    PUT    : Update employment record
    DELETE : Delete employment record
    """

    def get_object(self, pk):
        try:
            return EmploymentRecord.objects.get(pk=pk)
        except EmploymentRecord.DoesNotExist:
            return None

    def get(self, request, pk):
        employment_record = self.get_object(pk)

        if not employment_record:
            return Response(
                {
                    "success": False,
                    "message": "Employment record not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EmploymentRecordSerializer(employment_record)

        return Response(
            {
                "success": True,
                "message": "Employment record retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        employment_record = self.get_object(pk)

        if not employment_record:
            return Response(
                {
                    "success": False,
                    "message": "Employment record not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EmploymentRecordSerializer(
            employment_record,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Employment record updated successfully.",
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
        employment_record = self.get_object(pk)

        if not employment_record:
            return Response(
                {
                    "success": False,
                    "message": "Employment record not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        employment_record.delete()

        return Response(
            {
                "success": True,
                "message": "Employment record deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )





class ProjectRecordListCreateAPIView(APIView):
    """
    GET  : Get all project records
    POST : Create a new project record
    """

    def get(self, request):
        project_records = ProjectRecord.objects.all().order_by("-start_date")

        serializer = ProjectRecordSerializer(
            project_records,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": "Project records fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ProjectRecordSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Project record created successfully.",
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



class ProjectRecordRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Retrieve project record by ID
    PUT    : Update project record
    DELETE : Delete project record
    """

    def get_object(self, pk):
        try:
            return ProjectRecord.objects.get(pk=pk)
        except ProjectRecord.DoesNotExist:
            return None

    def get(self, request, pk):
        project_record = self.get_object(pk)

        if not project_record:
            return Response(
                {
                    "success": False,
                    "message": "Project record not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectRecordSerializer(project_record)

        return Response(
            {
                "success": True,
                "message": "Project record retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        project_record = self.get_object(pk)

        if not project_record:
            return Response(
                {
                    "success": False,
                    "message": "Project record not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectRecordSerializer(
            project_record,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Project record updated successfully.",
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
        project_record = self.get_object(pk)

        if not project_record:
            return Response(
                {
                    "success": False,
                    "message": "Project record not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        project_record.delete()

        return Response(
            {
                "success": True,
                "message": "Project record deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )





class ProjectScopeListCreateAPIView(APIView):
    """
    GET  : Get all project scopes
    POST : Create a new project scope
    """

    def get(self, request):
        project_scopes = ProjectScope.objects.all().order_by(
            "project",
            "scope"
        )

        serializer = ProjectScopeSerializer(
            project_scopes,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": "Project scopes fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ProjectScopeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Project scope created successfully.",
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


class ProjectScopeRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Retrieve project scope by ID
    PUT    : Update project scope
    DELETE : Delete project scope
    """

    def get_object(self, pk):
        try:
            return ProjectScope.objects.get(pk=pk)
        except ProjectScope.DoesNotExist:
            return None

    def get(self, request, pk):
        project_scope = self.get_object(pk)

        if not project_scope:
            return Response(
                {
                    "success": False,
                    "message": "Project scope not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectScopeSerializer(project_scope)

        return Response(
            {
                "success": True,
                "message": "Project scope retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        project_scope = self.get_object(pk)

        if not project_scope:
            return Response(
                {
                    "success": False,
                    "message": "Project scope not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectScopeSerializer(
            project_scope,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Project scope updated successfully.",
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
        project_scope = self.get_object(pk)

        if not project_scope:
            return Response(
                {
                    "success": False,
                    "message": "Project scope not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        project_scope.delete()

        return Response(
            {
                "success": True,
                "message": "Project scope deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )





class ScopeResponseListCreateAPIView(APIView):
    """
    GET  : Get all scope responses
    POST : Create a new scope response
    """

    def get(self, request):
        scope_responses = ScopeResponse.objects.all().order_by(
            "project_scope",
            "form_field",
            "repeat_group_key",
            "repeat_index",
        )

        serializer = ScopeResponseSerializer(
            scope_responses,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": "Scope responses fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ScopeResponseSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Scope response created successfully.",
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




class ScopeResponseRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Retrieve scope response by ID
    PUT    : Update scope response
    DELETE : Delete scope response
    """

    def get_object(self, pk):
        try:
            return ScopeResponse.objects.get(pk=pk)
        except ScopeResponse.DoesNotExist:
            return None

    def get(self, request, pk):
        scope_response = self.get_object(pk)

        if not scope_response:
            return Response(
                {
                    "success": False,
                    "message": "Scope response not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ScopeResponseSerializer(scope_response)

        return Response(
            {
                "success": True,
                "message": "Scope response retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        scope_response = self.get_object(pk)

        if not scope_response:
            return Response(
                {
                    "success": False,
                    "message": "Scope response not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ScopeResponseSerializer(
            scope_response,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Scope response updated successfully.",
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
        scope_response = self.get_object(pk)

        if not scope_response:
            return Response(
                {
                    "success": False,
                    "message": "Scope response not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        scope_response.delete()

        return Response(
            {
                "success": True,
                "message": "Scope response deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )



class ExposureLogListCreateAPIView(APIView):
    """
    GET  : Get all exposure logs
    POST : Create a new exposure log
    """

    def get(self, request):
        exposure_logs = ExposureLog.objects.all().order_by("-activity_date")

        serializer = ExposureLogSerializer(
            exposure_logs,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": "Exposure logs fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ExposureLogSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Exposure log created successfully.",
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



class ExposureLogRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Retrieve exposure log by ID
    PUT    : Update exposure log
    DELETE : Delete exposure log
    """

    def get_object(self, pk):
        try:
            return ExposureLog.objects.get(pk=pk)
        except ExposureLog.DoesNotExist:
            return None

    def get(self, request, pk):
        exposure_log = self.get_object(pk)

        if not exposure_log:
            return Response(
                {
                    "success": False,
                    "message": "Exposure log not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ExposureLogSerializer(exposure_log)

        return Response(
            {
                "success": True,
                "message": "Exposure log retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        exposure_log = self.get_object(pk)

        if not exposure_log:
            return Response(
                {
                    "success": False,
                    "message": "Exposure log not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ExposureLogSerializer(
            exposure_log,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Exposure log updated successfully.",
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
        exposure_log = self.get_object(pk)

        if not exposure_log:
            return Response(
                {
                    "success": False,
                    "message": "Exposure log not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        exposure_log.delete()

        return Response(
            {
                "success": True,
                "message": "Exposure log deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )





class ProfessionalAssignmentListCreateAPIView(APIView):
    """
    GET  : Get all professional assignments
    POST : Create a new professional assignment
    """

    def get(self, request):
        assignments = ProfessionalAssignment.objects.all().order_by("-start_date")

        serializer = ProfessionalAssignmentSerializer(
            assignments,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": "Professional assignments fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ProfessionalAssignmentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Professional assignment created successfully.",
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





class ProfessionalAssignmentRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Retrieve professional assignment by ID
    PUT    : Update professional assignment
    DELETE : Delete professional assignment
    """

    def get_object(self, pk):
        try:
            return ProfessionalAssignment.objects.get(pk=pk)
        except ProfessionalAssignment.DoesNotExist:
            return None

    def get(self, request, pk):
        assignment = self.get_object(pk)

        if not assignment:
            return Response(
                {
                    "success": False,
                    "message": "Professional assignment not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProfessionalAssignmentSerializer(assignment)

        return Response(
            {
                "success": True,
                "message": "Professional assignment retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        assignment = self.get_object(pk)

        if not assignment:
            return Response(
                {
                    "success": False,
                    "message": "Professional assignment not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProfessionalAssignmentSerializer(
            assignment,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Professional assignment updated successfully.",
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
        assignment = self.get_object(pk)

        if not assignment:
            return Response(
                {
                    "success": False,
                    "message": "Professional assignment not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        assignment.delete()

        return Response(
            {
                "success": True,
                "message": "Professional assignment deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )