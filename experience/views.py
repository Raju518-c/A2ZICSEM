from django.db import transaction
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status

from professionals.models import ProfessionalProfile

from .models import *
from .serializers import *

from catalog.models import FormField, ReferenceValue, ReferencevalueoptionSet, ScopeModule
from core.choices import DataClassification, ResumeVisibility, VerificationStatus
from evidence.models import EvidenceDocument
from professionals.models import ProfessionalProfile


def _get_or_create_employment_evidence_type(creator):
    option_set, _ = ReferencevalueoptionSet.objects.get_or_create(option_type="EVIDENCE_TYPE")
    evidence_type, _ = ReferenceValue.objects.get_or_create(
        option_set=option_set,
        code="EMPLOYMENT_PROOF",
        defaults={
            "label": "Employment Proof",
            "created_by": creator,
            "is_system": True,
            "is_active": True,
        },
    )
    return evidence_type


def _create_employment_evidence(professional, employment_record, evidence_file):
    if not evidence_file:
        return None

    evidence_type = _get_or_create_employment_evidence_type(professional.user)
    content_type = ContentType.objects.get_for_model(EmploymentRecord)
    return EvidenceDocument.objects.create(
        tenant=professional.tenant,
        professional=professional,
        content_type=content_type,
        object_id=employment_record.pk,
        evidence_type=evidence_type,
        file=evidence_file,
        data_classification=DataClassification.PROFESSIONAL,
        resume_visibility=ResumeVisibility.CLIENT_SPECIFIC,
        verification_status=VerificationStatus.EVIDENCE_UPLOADED,
        processing_status=EvidenceDocument.ProcessingStatus.UPLOADED,
    )


def _sync_employment_evidence_target(employment_record):
    """Keep EvidenceDocument.content_type/object_id pointing at whichever
    EmploymentRecord currently holds it. Needed because "evidence" can be
    set two ways: uploading a file (already points correctly at creation)
    or linking an existing EvidenceDocument id directly — the second path
    doesn't update the document's own generic-FK target on its own.
    """
    if not employment_record.evidence_id:
        return

    evidence_document = employment_record.evidence
    content_type = ContentType.objects.get_for_model(EmploymentRecord)
    if (
        evidence_document.content_type_id != content_type.id
        or evidence_document.object_id != employment_record.pk
    ):
        evidence_document.content_type = content_type
        evidence_document.object_id = employment_record.pk
        evidence_document.save(update_fields=["content_type", "object_id"])


@method_decorator(csrf_exempt, name='dispatch')
class EmploymentRecordListCreateAPIView(APIView):
    """
    GET  : Get all employment records. Optional ?professional=<id> filters
    to one professional's records.
    POST : Create employment records in bulk. professional_id is applied
    to every record; tenant is derived from the professional's own tenant
    and must not be sent. Saved atomically — if any record is invalid,
    none are created.

    Two ways to call POST:
    - JSON body: {"professional_id": X, "employment_records": [ {...}, {...} ]}
    - multipart/form-data (when attaching evidence files):
      professional_id: X
      employment_records: '[{...}, {...}]'  (employment_records JSON-encoded as a string)
      evidence_0: <file>  (optional, attaches to employment_records[0])
      evidence_1: <file>  (optional, attaches to employment_records[1], etc.)
    """

    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get(self, request):
        employment_records = EmploymentRecord.objects.all().order_by("-start_date")

        professional_id = request.query_params.get("professional")
        if professional_id:
            try:
                professional_id = int(professional_id)
            except (TypeError, ValueError):
                return Response(
                    {"success": False, "message": "professional query parameter must be a valid integer."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            employment_records = employment_records.filter(professional_id=professional_id)


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
    
    @extend_schema(request=EmploymentRecordSerializer(many=True))
    def post(self, request):
        professional_id = request.data.get("professional_id")
        employment_records = request.data.get("employment_records")

        if isinstance(employment_records, str):
            try:
                employment_records = json.loads(employment_records)
            except (TypeError, ValueError):
                return Response(
                    {
                        "success": False,
                        "message": "employment_records must be valid JSON.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if not professional_id or not isinstance(employment_records, list):
            return Response(
                {
                    "success": False,
                    "message": "professional_id and employment_records (list) are required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            professional_id = int(professional_id)
        except (TypeError, ValueError):
            return Response(
                {"success": False, "message": "professional_id must be a valid integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            professional = ProfessionalProfile.objects.get(id=professional_id)
        except ProfessionalProfile.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Professional not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        for record in employment_records:
            record["professional"] = professional_id
            record["tenant"] = professional.tenant_id

        serializer = EmploymentRecordSerializer(data=employment_records, many=True)

        if serializer.is_valid():
            with transaction.atomic():
                created_records = serializer.save()

                for index, employment_record in enumerate(created_records):
                    evidence_file = request.FILES.get(f"evidence_{index}")
                    evidence_document = _create_employment_evidence(
                        professional, employment_record, evidence_file
                    )
                    if evidence_document:
                        employment_record.evidence = evidence_document
                        employment_record.save(update_fields=["evidence"])

                    _sync_employment_evidence_target(employment_record)

            output_serializer = EmploymentRecordSerializer(created_records, many=True)

            return Response(
                {
                    "success": True,
                    "message": "Employment records created successfully.",
                    "data": output_serializer.data,
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
class EmploymentRecordRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Retrieve employment record by ID
    PUT    : Update employment record (partial). Any field may be sent,
    including "professional" (re-derives tenant to match) and "evidence"
    (links an existing EvidenceDocument by id). To upload a new evidence
    file instead of linking an existing one, send multipart/form-data with
    an "evidence_file" field — it's uploaded and linked in the same call.
    DELETE : Delete employment record
    """

    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
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
    
    @extend_schema(request=EmploymentRecordSerializer)
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

        data = request.data
        professional_id = data.get("professional")
        if professional_id:
            try:
                professional_id = int(professional_id)
            except (TypeError, ValueError):
                return Response(
                    {"success": False, "message": "professional must be a valid integer."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                professional = ProfessionalProfile.objects.get(id=professional_id)
            except ProfessionalProfile.DoesNotExist:
                return Response(
                    {
                        "success": False,
                        "message": "Professional not found.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            if hasattr(data, "_mutable"):
                data._mutable = True
            data["tenant"] = professional.tenant_id

        evidence_file = request.FILES.get("evidence_file")

        serializer = EmploymentRecordSerializer(
            employment_record,
            data=data,
            partial=True,
        )

        if serializer.is_valid():
            updated_record = serializer.save()

            if evidence_file:
                evidence_professional = professional if professional_id else updated_record.professional
                evidence_document = _create_employment_evidence(
                    evidence_professional, updated_record, evidence_file
                )
                updated_record.evidence = evidence_document
                updated_record.save(update_fields=["evidence"])

            _sync_employment_evidence_target(updated_record)

            output_serializer = EmploymentRecordSerializer(updated_record)
            

            return Response(
                {
                    "success": True,
                    "message": "Employment record updated successfully.",
                    "data": output_serializer.data,
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




@method_decorator(csrf_exempt, name='dispatch')
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
    
    @extend_schema(request=ProjectRecordSerializer)
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


@method_decorator(csrf_exempt, name='dispatch')
class BulkProjectRecordCreateAPIView(APIView):
    """
    POST : Create multiple project records with nested scopes and scope responses.
    """

    @extend_schema(request=BulkProjectRecordSerializer)
    def post(self, request):
        user = getattr(request, "user", None)
        professional_profile_id = (
            request.data.get("professional_profile")
            or request.data.get("professional_profile_id")
        )
        professional = None
        tenant = None

        if professional_profile_id:
            professional = ProfessionalProfile.objects.filter(pk=professional_profile_id).first()
            if professional:
                tenant = getattr(professional, "tenant", None)

        if not professional:
            return Response(
                {
                    "success": False,
                    "message": "ProfessionalProfile PK is required for bulk project creation.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not tenant:
            return Response(
                {
                    "success": False,
                    "message": "Tenant context is required for bulk project creation.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = BulkProjectRecordSerializer(
            data=request.data,
            context={
                "tenant": tenant,
                "professional": professional,
                "created_by": user,
            },
        )

        if serializer.is_valid():
            created_records = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Project records created successfully.",
                    "data": ProjectRecordSerializer(created_records, many=True).data,
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
    
    @extend_schema(request=ProjectRecordSerializer)
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




@method_decorator(csrf_exempt, name='dispatch')
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
    
    @extend_schema(request=ProjectScopeSerializer)
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

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ProjectScopeDynamicFormAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return ProjectScope.objects.select_related("scope", "project", "project__professional").get(pk=pk)
        except ProjectScope.DoesNotExist:
            return None

    def get(self, request, pk):
        project_scope = self.get_object(pk)
        if not project_scope:
            return Response(
                {"success": False, "message": "Project scope not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        scope = project_scope.scope
        form_fields = (
            FormField.objects.filter(
                form_module__scope_modules__scope=scope,
                is_active=True,
            )
            .select_related("form_module")
            .distinct()
            .order_by("form_module__scope_modules__sequence", "sequence")
        )
        response_lookup = {
            response.form_field_id: response
            for response in ScopeResponse.objects.filter(project_scope=project_scope).select_related("form_field")
        }
        field_serializer = ScopeFormFieldSerializer(
            form_fields,
            many=True,
            context={"response_lookup": response_lookup},
        )

        return Response(
            {
                "success": True,
                "message": "Dynamic scope form fetched successfully.",
                "data": {
                    "project_scope": {
                        "id": project_scope.pk,
                        "status": project_scope.status,
                        "verification_status": project_scope.verification_status,
                    },
                    "scope": {
                        "id": scope.pk,
                        "code": scope.code,
                        "scope_name": scope.scope_name,
                        "industry": {
                            "id": scope.industry_id,
                            "code": scope.industry.code if scope.industry else None,
                            "label": scope.industry.label if scope.industry else None,
                        } if scope.industry else None,
                    },
                    "form_fields": field_serializer.data,
                },
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, pk):
        project_scope = self.get_object(pk)
        if not project_scope:
            return Response(
                {"success": False, "message": "Project scope not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        responses_payload = request.data.get("responses", [])
        if not isinstance(responses_payload, list):
            return Response(
                {"success": False, "message": "responses must be a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        scope = project_scope.scope
        saved_responses = []
        with transaction.atomic():
            for response_payload in responses_payload:
                field_code = response_payload.get("field_code")
                if not field_code:
                    continue

                form_field = (
                    FormField.objects.filter(
                        field_code__iexact=field_code,
                        is_active=True,
                    )
                    .filter(form_module__scope_modules__scope=scope)
                    .distinct()
                    .first()
                )
                if not form_field:
                    return Response(
                        {
                            "success": False,
                            "message": f"Form field '{field_code}' is not assigned to this scope.",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                response_obj, _ = ScopeResponse.objects.update_or_create(
                    project_scope=project_scope,
                    form_field=form_field,
                    defaults={
                        "tenant": project_scope.tenant,
                        "value": response_payload.get("value"),
                        "verification_status": VerificationStatus.SELF_DECLARED,
                    },
                )
                saved_responses.append(response_obj)

        return Response(
            {
                "success": True,
                "message": "Scope responses saved successfully.",
                "data": {
                    "count": len(saved_responses),
                    "project_scope_id": project_scope.pk,
                },
            },
            status=status.HTTP_200_OK,
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
    
    @extend_schema(request=ProjectScopeSerializer)
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




@method_decorator(csrf_exempt, name='dispatch')
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
    
    @extend_schema(request=ScopeResponseSerializer)
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



@method_decorator(csrf_exempt, name='dispatch')
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
    
    @extend_schema(request=ScopeResponseSerializer)
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

@method_decorator(csrf_exempt, name='dispatch')
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
    
    @extend_schema(request=ExposureLogSerializer)
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


@method_decorator(csrf_exempt, name='dispatch')
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
    
    @extend_schema(request=ExposureLogSerializer)
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




@method_decorator(csrf_exempt, name='dispatch')
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
    
    @extend_schema(request=ProfessionalAssignmentSerializer)
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




@method_decorator(csrf_exempt, name='dispatch')
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
        

class ValidateExperienceTabAPIView(APIView):

    def post(self, request):

        employment_errors = []
        project_errors = []

        employment_records = request.data.get(
            "employment_records", []
        )

        project_records = request.data.get(
            "project_records", []
        )

        # Employment Validation
        for emp_index, emp in enumerate(employment_records):

            serializer = EmploymentRecordSerializer(
                data=emp,
                context={"request": request}
            )

            if not serializer.is_valid():
                employment_errors.append({
                    "index": emp_index,
                    "errors": serializer.errors
                })

        # Project Validation
        for proj_index, project in enumerate(project_records):

            current_project_errors = {}

            project_serializer = ProjectRecordSerializer(
                data=project,
                context={"request": request}
            )

            if not project_serializer.is_valid():
                current_project_errors["errors"] = (
                    project_serializer.errors
                )

            scope_errors = []

            for scope_index, scope_data in enumerate(
                project.get("ProjectScope", [])
            ):

                scope_serializer = ProjectScopeSerializer(
                    data=scope_data,
                    context={"request": request}
                )

                current_scope_errors = {}

                if not scope_serializer.is_valid():
                    current_scope_errors["errors"] = (
                        scope_serializer.errors
                    )

                response_errors = []

                for response_index, response_data in enumerate(
                    scope_data.get("ScopeResponse", [])
                ):

                    response_serializer = (
                        ScopeResponseSerializer(
                            data=response_data,
                            context={"request": request}
                        )
                    )

                    if not response_serializer.is_valid():
                        response_errors.append({
                            "index": response_index,
                            "errors": response_serializer.errors
                        })

                if response_errors:
                    current_scope_errors[
                        "scope_responses"
                    ] = response_errors

                if current_scope_errors:
                    current_scope_errors[
                        "index"
                    ] = scope_index

                    scope_errors.append(
                        current_scope_errors
                    )

            if current_project_errors or scope_errors:

                project_errors.append({
                    "index": proj_index,
                    **current_project_errors,
                    "project_scopes": scope_errors
                })

        if employment_errors or project_errors:

            return Response(
                {
                    "valid": False,
                    "errors": {
                        "employment_records":
                            employment_errors,
                        "project_records":
                            project_errors
                    }
                },
                status=400
            )

        return Response(
            {
                "valid": True,
                "message":
                    "All records validated successfully."
            }
        )


        