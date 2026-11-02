# training/combined_views.py

from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from accounts.models import *

from .serializers import *
from django.db.models import ProtectedError
from rest_framework import status, serializers

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ContentAssignment

def require_platform_admin(user):
    # Replace with the actual platform-role permission check in this project.
    if not (getattr(user, "is_superuser", False) or getattr(user, "is_staff", False)):
        raise PermissionDenied("Platform administrator permission required.")


def resolve_tenant_id(user):
    tenant_id = getattr(user, "tenant_id", None)
    if tenant_id is None:
        tenant_id = getattr(getattr(user, "tenant", None), "pk", None)
    if tenant_id is None:
        raise PermissionDenied("No tenant is associated with this user. Update resolve_tenant_id() for your membership model.")
    return tenant_id



def api_error(exc):
    if isinstance(exc, IntegrityError):
        return Response(
            {"status": False, "message": "A database constraint was violated. Check for duplicate codes/sequences or related records."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    raise exc

def validate_id_list(data, label):
    field = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=False)
    ids = field.run_validation(data)
    if len(ids) != len(set(ids)):
        raise ValidationError({label: "Duplicate IDs are not allowed."})
    return ids


def check_all_ids_exist(model, ids, label):
    existing = set(model.objects.filter(pk__in=ids).values_list("pk", flat=True))
    missing = sorted(set(ids) - existing)
    if missing:
        raise ValidationError({f"{label}_not_found": missing})


class TrainingProgramWithModulesListCreateAPIView(APIView):
    """GET/POST /program-with-modules/; DELETE on this URL bulk-deletes programs."""
    permission_classes = [AllowAny]

    def get(self, request):
        require_platform_admin(request.user)
        qs = TrainingProgram.objects.prefetch_related("modules").order_by("id")
        return Response({"status": True, "results": TrainingProgramWithModulesReadSerializer(qs, many=True).data})

    def post(self, request):
        require_platform_admin(request.user)
        if not isinstance(request.data, dict):
            raise ValidationError("Request body must be a JSON object.")
        if "program" not in request.data:
            raise ValidationError({"program": "This field is required."})
        if not isinstance(request.data["program"], dict):
            raise ValidationError({"program": "Must be an object."})

        modules_payload = request.data.get("Modules", [])
        if not isinstance(modules_payload, list):
            raise ValidationError({"Modules": "Must be a list."})

        program_ser = TrainingProgramFieldsSerializer(data=request.data["program"])
        program_ser.is_valid(raise_exception=True)
        modules_ser = TrainingModuleFieldsSerializer(data=modules_payload, many=True)
        modules_ser.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                program = program_ser.save()
                for module_data in modules_ser.validated_data:
                    module_data.pop("id", None)
                    TrainingModule.objects.create(program=program, **module_data)
        except IntegrityError:
            raise ValidationError("Program/module data violates a database constraint. Check duplicate codes or sequences.")

        program.refresh_from_db()
        return Response(TrainingProgramWithModulesReadSerializer(program).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        """Accepts a JSON array of program IDs, e.g. [1, 2, 5]."""
        require_platform_admin(request.user)
        ids = request.data
        if not isinstance(ids, list) or not ids:
            raise ValidationError("Request body must be a non-empty JSON array of program IDs, e.g. [1, 2, 5].")
        id_serializer = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=False)
        ids = id_serializer.run_validation(ids)
        if len(ids) != len(set(ids)):
            raise ValidationError("Duplicate program IDs are not allowed.")

        programs = list(TrainingProgram.objects.filter(pk__in=ids).order_by("pk"))
        found_ids = {obj.pk for obj in programs}
        missing_ids = sorted(set(ids) - found_ids)
        if missing_ids:
            raise ValidationError({"program_ids_not_found": missing_ids})

        try:
            with transaction.atomic():
                for program in programs:
                    # Explicitly remove modules first; the transaction rolls back if the
                    # program is protected by other related records.
                    TrainingModule.objects.filter(program=program).delete()
                    program.delete()
        except (IntegrityError, ProtectedError):
            raise ValidationError("One or more programs are referenced by other records and cannot be deleted. Retire them instead.")

        return Response({"status": True, "deleted_program_ids": ids}, status=status.HTTP_200_OK)


class TrainingProgramWithModulesDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        return get_object_or_404(TrainingProgram.objects.prefetch_related("modules"), pk=pk)

    def get(self, request, pk):
        require_platform_admin(request.user)
        return Response(TrainingProgramWithModulesReadSerializer(self.get_object(pk)).data)

    def put(self, request, pk):
        require_platform_admin(request.user)
        program = self.get_object(pk)
        if not isinstance(request.data, dict):
            raise ValidationError("Request body must be a JSON object.")
        if not isinstance(request.data.get("program"), dict):
            raise ValidationError({"program": "This field is required and must be an object."})

        allowed_keys = {"program", "NewModules", "UpdateExistingModules", "DeleteExistingModuleIDs"}
        unknown = set(request.data.keys()) - allowed_keys
        if unknown:
            raise ValidationError({"unknown_fields": sorted(unknown)})

        program_ser = TrainingProgramFieldsSerializer(program, data=request.data["program"], partial=True)
        program_ser.is_valid(raise_exception=True)

        new_payload = request.data.get("NewModules", [])
        update_payload = request.data.get("UpdateExistingModules", [])
        delete_payload = request.data.get("DeleteExistingModuleIDs", [])
        if not isinstance(new_payload, list):
            raise ValidationError({"NewModules": "Must be a list."})
        if not isinstance(update_payload, list):
            raise ValidationError({"UpdateExistingModules": "Must be a list."})
        if not isinstance(delete_payload, list):
            raise ValidationError({"DeleteExistingModuleIDs": "Must be a list of module IDs."})

        new_ser = TrainingModuleFieldsSerializer(data=new_payload, many=True)
        new_ser.is_valid(raise_exception=True)
        update_ser = TrainingModuleUpdateItemSerializer(data=update_payload, many=True)
        update_ser.is_valid(raise_exception=True)
        delete_ser = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=True)
        delete_ids = delete_ser.run_validation(delete_payload)

        update_items = update_ser.validated_data
        update_ids = [item["id"] for item in update_items]
        if len(update_ids) != len(set(update_ids)):
            raise ValidationError({"UpdateExistingModules": "A module ID may appear only once."})
        if len(delete_ids) != len(set(delete_ids)):
            raise ValidationError({"DeleteExistingModuleIDs": "Duplicate module IDs are not allowed."})
        overlap = set(update_ids) & set(delete_ids)
        if overlap:
            raise ValidationError({"module_ids": f"These module IDs cannot be updated and deleted in the same request: {sorted(overlap)}"})

        all_existing_ids = set(TrainingModule.objects.filter(program=program).values_list("id", flat=True))
        requested_existing_ids = set(update_ids) | set(delete_ids)
        invalid_ids = sorted(requested_existing_ids - all_existing_ids)
        if invalid_ids:
            raise ValidationError({"invalid_module_ids": invalid_ids, "detail": "Every updated/deleted module must belong to this program."})

        try:
            with transaction.atomic():
                program = program_ser.save()
                for item in update_items:
                    item = dict(item)
                    module_id = item.pop("id")
                    module = TrainingModule.objects.get(pk=module_id, program=program)
                    module_ser = TrainingModuleFieldsSerializer(module, data=item, partial=True)
                    module_ser.is_valid(raise_exception=True)
                    module_ser.save()
                for module_data in new_ser.validated_data:
                    module_data = dict(module_data)
                    module_data.pop("id", None)
                    TrainingModule.objects.create(program=program, **module_data)
                if delete_ids:
                    TrainingModule.objects.filter(program=program, pk__in=delete_ids).delete()
        except IntegrityError:
            raise ValidationError("Program/module data violates a database constraint. Check duplicate codes or sequences.")

        program.refresh_from_db()
        return Response(TrainingProgramWithModulesReadSerializer(program).data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        return self.put(request, pk)

    def delete(self, request, pk):
        require_platform_admin(request.user)
        program = self.get_object(pk)
        try:
            with transaction.atomic():
                TrainingModule.objects.filter(program=program).delete()
                program.delete()
        except (IntegrityError, ProtectedError):
            raise ValidationError("This program is referenced by other records and cannot be deleted. Retire it instead.")
        return Response(status=status.HTTP_204_NO_CONTENT)



class QuestionBankWithOptionsListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        require_platform_admin(request.user)
        qs = QuestionBank.objects.prefetch_related("options").order_by("id")
        return Response({"status": True, "results": QuestionReadSerializer(qs, many=True).data})

    def post(self, request):
        """POST {question: {...}, Options: [{...}, ...]} or {questions: [{question, Options}, ...]}."""
        require_platform_admin(request.user)
        bulk = isinstance(request.data, dict) and "questions" in request.data
        payloads = request.data.get("questions") if bulk else [request.data]
        if not isinstance(payloads, list) or not payloads:
            raise ValidationError({"questions": "Must be a non-empty list."})
        created = []
        try:
            with transaction.atomic():
                for item in payloads:
                    if not isinstance(item, dict) or not isinstance(item.get("question"), dict):
                        raise ValidationError({"question": "Each item must contain a question object."})
                    options = item.get("Options", [])
                    if not isinstance(options, list):
                        raise ValidationError({"Options": "Must be a list."})
                    qser = QuestionFieldsSerializer(data=item["question"])
                    qser.is_valid(raise_exception=True)
                    oser = QuestionOptionFieldsSerializer(data=options, many=True)
                    oser.is_valid(raise_exception=True)
                    question = qser.save()
                    for option_data in oser.validated_data:
                        QuestionOption.objects.create(question=question, **option_data)
                    created.append(question)
        except IntegrityError:
            raise ValidationError("Question/option data violates a database constraint.")
        output = QuestionReadSerializer(created, many=True).data
        return Response(output if bulk else output[0], status=201)

    def delete(self, request):
        """Bulk delete: body [question_id, ...]; options are deleted with each question."""
        require_platform_admin(request.user)
        ids = validate_id_list(request.data, "question_ids")
        check_all_ids_exist(QuestionBank, ids, "question_ids")
        try:
            with transaction.atomic():
                # Explicit child deletion makes the intended cascade clear.
                QuestionOption.objects.filter(question_id__in=ids).delete()
                QuestionBank.objects.filter(pk__in=ids).delete()
        except (IntegrityError, ProtectedError):
            raise ValidationError("One or more questions are referenced by other records and cannot be deleted.")
        return Response({"status": True, "deleted_question_ids": ids})


class QuestionBankWithOptionsDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        return get_object_or_404(QuestionBank.objects.prefetch_related("options"), pk=pk)

    def get(self, request, pk):
        require_platform_admin(request.user)
        return Response(QuestionReadSerializer(self.get_object(pk)).data)

    def put(self, request, pk):
        require_platform_admin(request.user)
        question = self.get_object(pk)
        if not isinstance(request.data, dict) or not isinstance(request.data.get("question"), dict):
            raise ValidationError({"question": "A question object is required."})
        allowed = {"question", "NewOptions", "UpdateExistingOptions", "DeleteExistingOptionIDs"}
        unknown = set(request.data) - allowed
        if unknown:
            raise ValidationError({"unknown_fields": sorted(unknown)})
        new_data = request.data.get("NewOptions", [])
        update_data = request.data.get("UpdateExistingOptions", [])
        delete_ids = request.data.get("DeleteExistingOptionIDs", [])
        if not isinstance(new_data, list) or not isinstance(update_data, list) or not isinstance(delete_ids, list):
            raise ValidationError("NewOptions, UpdateExistingOptions and DeleteExistingOptionIDs must be lists.")
        qser = QuestionFieldsSerializer(question, data=request.data["question"], partial=True)
        qser.is_valid(raise_exception=True)
        nser = QuestionOptionFieldsSerializer(data=new_data, many=True)
        nser.is_valid(raise_exception=True)
        user = QuestionOptionUpdateSerializer(data=update_data, many=True)
        user.is_valid(raise_exception=True)
        delete_ids = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=True).run_validation(delete_ids)
        update_ids = [x["id"] for x in user.validated_data]
        if len(update_ids) != len(set(update_ids)) or len(delete_ids) != len(set(delete_ids)):
            raise ValidationError("Duplicate option IDs are not allowed.")
        if set(update_ids) & set(delete_ids):
            raise ValidationError("An option cannot be updated and deleted in the same request.")
        owned = set(QuestionOption.objects.filter(question=question).values_list("id", flat=True))
        invalid = sorted((set(update_ids) | set(delete_ids)) - owned)
        if invalid:
            raise ValidationError({"invalid_option_ids": invalid, "detail": "Options must belong to this question."})
        try:
            with transaction.atomic():
                question = qser.save()
                for item in user.validated_data:
                    item = dict(item); option_id = item.pop("id")
                    option = QuestionOption.objects.get(pk=option_id, question=question)
                    ser = QuestionOptionFieldsSerializer(option, data=item, partial=True)
                    ser.is_valid(raise_exception=True); ser.save()
                for item in nser.validated_data:
                    QuestionOption.objects.create(question=question, **item)
                if delete_ids:
                    QuestionOption.objects.filter(question=question, pk__in=delete_ids).delete()
        except IntegrityError:
            raise ValidationError("Question/option data violates a database constraint.")
        question.refresh_from_db()
        return Response(QuestionReadSerializer(question).data)

    def patch(self, request, pk):
        return self.put(request, pk)

    def delete(self, request, pk):
        require_platform_admin(request.user)
        question = self.get_object(pk)
        try:
            with transaction.atomic():
                QuestionOption.objects.filter(question=question).delete()
                question.delete()
        except (IntegrityError, ProtectedError):
            raise ValidationError("This question is referenced by other records and cannot be deleted.")
        return Response(status=204)


class TrainingAssessmentWithConfigsListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        require_platform_admin(request.user)
        qs = TrainingAssessment.objects.prefetch_related("question_configs").order_by("id")
        return Response({"status": True, "results": AssessmentReadSerializer(qs, many=True).data})

    def post(self, request):
        """POST {assessment: {...}, Configs: [{...}, ...]} or {assessments: [...]} for bulk create."""
        require_platform_admin(request.user)
        bulk = isinstance(request.data, dict) and "assessments" in request.data
        payloads = request.data.get("assessments") if bulk else [request.data]
        if not isinstance(payloads, list) or not payloads:
            raise ValidationError({"assessments": "Must be a non-empty list."})
        created = []
        try:
            with transaction.atomic():
                for item in payloads:
                    if not isinstance(item, dict) or not isinstance(item.get("assessment"), dict):
                        raise ValidationError({"assessment": "Each item must contain an assessment object."})
                    configs = item.get("Configs", [])
                    if not isinstance(configs, list):
                        raise ValidationError({"Configs": "Must be a list."})
                    pser = AssessmentFieldsSerializer(data=item["assessment"]); pser.is_valid(raise_exception=True)
                    cser = AssessmentConfigFieldsSerializer(data=configs, many=True); cser.is_valid(raise_exception=True)
                    assessment = pser.save()
                    for config_data in cser.validated_data:
                        AssessmentQuestionConfig.objects.create(assessment=assessment, **config_data)
                    created.append(assessment)
        except IntegrityError:
            raise ValidationError("Assessment/configuration data violates a database constraint.")
        output = AssessmentReadSerializer(created, many=True).data
        return Response(output if bulk else output[0], status=201)

    def delete(self, request):
        """Bulk delete: body [assessment_id, ...]; configurations are deleted with each assessment."""
        require_platform_admin(request.user)
        ids = validate_id_list(request.data, "assessment_ids")
        check_all_ids_exist(TrainingAssessment, ids, "assessment_ids")
        try:
            with transaction.atomic():
                AssessmentQuestionConfig.objects.filter(assessment_id__in=ids).delete()
                TrainingAssessment.objects.filter(pk__in=ids).delete()
        except (IntegrityError, ProtectedError):
            raise ValidationError("One or more assessments are referenced by other records and cannot be deleted.")
        return Response({"status": True, "deleted_assessment_ids": ids})


class TrainingAssessmentWithConfigsDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        return get_object_or_404(TrainingAssessment.objects.prefetch_related("question_configs"), pk=pk)

    def get(self, request, pk):
        require_platform_admin(request.user)
        return Response(AssessmentReadSerializer(self.get_object(pk)).data)

    def put(self, request, pk):
        require_platform_admin(request.user)
        assessment = self.get_object(pk)
        if not isinstance(request.data, dict) or not isinstance(request.data.get("assessment"), dict):
            raise ValidationError({"assessment": "An assessment object is required."})
        allowed = {"assessment", "NewConfigs", "UpdateExistingConfigs", "DeleteExistingConfigIDs"}
        unknown = set(request.data) - allowed
        if unknown:
            raise ValidationError({"unknown_fields": sorted(unknown)})
        new_data = request.data.get("NewConfigs", [])
        update_data = request.data.get("UpdateExistingConfigs", [])
        delete_ids = request.data.get("DeleteExistingConfigIDs", [])
        if not isinstance(new_data, list) or not isinstance(update_data, list) or not isinstance(delete_ids, list):
            raise ValidationError("NewConfigs, UpdateExistingConfigs and DeleteExistingConfigIDs must be lists.")
        pser = AssessmentFieldsSerializer(assessment, data=request.data["assessment"], partial=True); pser.is_valid(raise_exception=True)
        nser = AssessmentConfigFieldsSerializer(data=new_data, many=True); nser.is_valid(raise_exception=True)
        user = AssessmentConfigUpdateSerializer(data=update_data, many=True); user.is_valid(raise_exception=True)
        delete_ids = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=True).run_validation(delete_ids)
        update_ids = [x["id"] for x in user.validated_data]
        if len(update_ids) != len(set(update_ids)) or len(delete_ids) != len(set(delete_ids)):
            raise ValidationError("Duplicate configuration IDs are not allowed.")
        if set(update_ids) & set(delete_ids):
            raise ValidationError("A configuration cannot be updated and deleted in the same request.")
        owned = set(AssessmentQuestionConfig.objects.filter(assessment=assessment).values_list("id", flat=True))
        invalid = sorted((set(update_ids) | set(delete_ids)) - owned)
        if invalid:
            raise ValidationError({"invalid_config_ids": invalid, "detail": "Configurations must belong to this assessment."})
        try:
            with transaction.atomic():
                assessment = pser.save()
                for item in user.validated_data:
                    item = dict(item); config_id = item.pop("id")
                    config = AssessmentQuestionConfig.objects.get(pk=config_id, assessment=assessment)
                    ser = AssessmentConfigFieldsSerializer(config, data=item, partial=True)
                    ser.is_valid(raise_exception=True); ser.save()
                for item in nser.validated_data:
                    AssessmentQuestionConfig.objects.create(assessment=assessment, **item)
                if delete_ids:
                    AssessmentQuestionConfig.objects.filter(assessment=assessment, pk__in=delete_ids).delete()
        except IntegrityError:
            raise ValidationError("Assessment/configuration data violates a database constraint.")
        assessment.refresh_from_db()
        return Response(AssessmentReadSerializer(assessment).data)

    def patch(self, request, pk):
        return self.put(request, pk)

    def delete(self, request, pk):
        require_platform_admin(request.user)
        assessment = self.get_object(pk)
        try:
            with transaction.atomic():
                AssessmentQuestionConfig.objects.filter(assessment=assessment).delete()
                assessment.delete()
        except (IntegrityError, ProtectedError):
            raise ValidationError("This assessment is referenced by other records and cannot be deleted.")
        return Response(status=204)


class TenantTrainingProgramImportAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        tenant_id = resolve_tenant_id(request.user)
        qs = TenantTrainingProgram.objects.filter(tenant_id=tenant_id).select_related("master_program").order_by("id")
        data = []
        for obj in qs:
            row = TenantTrainingProgramFieldsSerializer(obj).data
            row.update({"imported_by": obj.imported_by_id, "tenant": obj.tenant_id})
            data.append(row)
        return Response({"status": True, "results": data})

    def post(self, request):
        tenant_id = resolve_tenant_id(request.user)
        bulk = isinstance(request.data, dict) and "items" in request.data
        payload = request.data.get("items") if bulk else [request.data]
        if not isinstance(payload, list) or not payload:
            raise ValidationError({"items": "Must be a non-empty list."})
        created = []
        try:
            with transaction.atomic():
                for item in payload:
                    ser = TenantTrainingProgramFieldsSerializer(data=item); ser.is_valid(raise_exception=True)
                    master = ser.validated_data["master_program"]
                    obj = TenantTrainingProgram.objects.create(
                        tenant_id=tenant_id, master_program=master,
                        imported_version=ser.validated_data.get("imported_version", master.version),
                        imported_by=request.user, is_active=ser.validated_data.get("is_active", True),
                    )
                    created.append(obj)
        except IntegrityError:
            raise ValidationError("One or more programs are already imported for this tenant or violate a database constraint.")
        data = []
        for obj in created:
            row = TenantTrainingProgramFieldsSerializer(obj).data
            row.update({"imported_by": obj.imported_by_id, "tenant": obj.tenant_id})
            data.append(row)
        return Response(data if bulk else data[0], status=201)

    def delete(self, request):
        tenant_id = resolve_tenant_id(request.user)
        ids = validate_id_list(request.data, "tenant_program_ids")
        existing = set(TenantTrainingProgram.objects.filter(tenant_id=tenant_id, pk__in=ids).values_list("pk", flat=True))
        missing = sorted(set(ids) - existing)
        if missing:
            raise ValidationError({"tenant_program_ids_not_found_for_tenant": missing})
        try:
            with transaction.atomic():
                TenantTrainingProgram.objects.filter(tenant_id=tenant_id, pk__in=ids).delete()
        except (IntegrityError, ProtectedError):
            raise ValidationError("One or more imported programs are referenced by tenant training records and cannot be deleted.")
        return Response({"status": True, "deleted_tenant_program_ids": ids})


class TenantTrainingProgramImportDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def put(self, request, pk):
        tenant_id = resolve_tenant_id(request.user)
        obj = get_object_or_404(TenantTrainingProgram, pk=pk, tenant_id=tenant_id)
        ser = TenantTrainingProgramFieldsSerializer(obj, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                obj = ser.save()
        except IntegrityError:
            raise ValidationError("Updated tenant program violates a database constraint.")
        row = TenantTrainingProgramFieldsSerializer(obj).data
        row.update({"imported_by": obj.imported_by_id, "tenant": obj.tenant_id})
        return Response(row)

    def delete(self, request, pk):
        tenant_id = resolve_tenant_id(request.user)
        obj = get_object_or_404(TenantTrainingProgram, pk=pk, tenant_id=tenant_id)
        try:
            with transaction.atomic():
                obj.delete()
        except (IntegrityError, ProtectedError):
            raise ValidationError("This imported program is referenced by tenant training records and cannot be deleted.")
        return Response(status=204)


class TenantAssessmentImportAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        tenant_id = resolve_tenant_id(request.user)
        qs = TenantAssessment.objects.filter(tenant_id=tenant_id).select_related("tenant_program", "master_assessment").order_by("id")
        data = []
        for obj in qs:
            row = TenantAssessmentFieldsSerializer(obj).data
            row.update({"imported_by": obj.imported_by_id, "tenant": obj.tenant_id})
            data.append(row)
        return Response({"status": True, "results": data})

    def post(self, request):
        tenant_id = resolve_tenant_id(request.user)
        bulk = isinstance(request.data, dict) and "items" in request.data
        payload = request.data.get("items") if bulk else [request.data]
        if not isinstance(payload, list) or not payload:
            raise ValidationError({"items": "Must be a non-empty list."})
        created = []
        try:
            with transaction.atomic():
                for item in payload:
                    ser = TenantAssessmentFieldsSerializer(data=item); ser.is_valid(raise_exception=True)
                    data = ser.validated_data
                    tenant_program = get_object_or_404(TenantTrainingProgram, pk=data["tenant_program"].pk, tenant_id=tenant_id, is_active=True)
                    assessment = data["master_assessment"]
                    if tenant_program.master_program_id != assessment.program_id:
                        raise ValidationError("Assessment must belong to the selected imported program.")
                    obj = TenantAssessment.objects.create(
                        tenant_id=tenant_id, tenant_program=tenant_program,
                        master_assessment=assessment, imported_by=request.user,
                        is_active=data.get("is_active", True),
                    )
                    created.append(obj)
        except IntegrityError:
            raise ValidationError("One or more assessments are already imported for this tenant or violate a database constraint.")
        output = []
        for obj in created:
            row = TenantAssessmentFieldsSerializer(obj).data
            row.update({"imported_by": obj.imported_by_id, "tenant": obj.tenant_id})
            output.append(row)
        return Response(output if bulk else output[0], status=201)

    def delete(self, request):
        tenant_id = resolve_tenant_id(request.user)
        ids = validate_id_list(request.data, "tenant_assessment_ids")
        existing = set(TenantAssessment.objects.filter(tenant_id=tenant_id, pk__in=ids).values_list("pk", flat=True))
        missing = sorted(set(ids) - existing)
        if missing:
            raise ValidationError({"tenant_assessment_ids_not_found_for_tenant": missing})
        try:
            with transaction.atomic():
                TenantAssessment.objects.filter(tenant_id=tenant_id, pk__in=ids).delete()
        except (IntegrityError, ProtectedError):
            raise ValidationError("One or more imported assessments are referenced by attempts and cannot be deleted.")
        return Response({"status": True, "deleted_tenant_assessment_ids": ids})


class TenantAssessmentImportDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def put(self, request, pk):
        tenant_id = resolve_tenant_id(request.user)
        obj = get_object_or_404(TenantAssessment, pk=pk, tenant_id=tenant_id)
        ser = TenantAssessmentFieldsSerializer(obj, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        if "tenant_program" in data:
            get_object_or_404(TenantTrainingProgram, pk=data["tenant_program"].pk, tenant_id=tenant_id)
        try:
            with transaction.atomic():
                obj = ser.save()
        except IntegrityError:
            raise ValidationError("Updated tenant assessment violates a database constraint.")
        row = TenantAssessmentFieldsSerializer(obj).data
        row.update({"imported_by": obj.imported_by_id, "tenant": obj.tenant_id})
        return Response(row)

    def delete(self, request, pk):
        tenant_id = resolve_tenant_id(request.user)
        obj = get_object_or_404(TenantAssessment, pk=pk, tenant_id=tenant_id)
        try:
            with transaction.atomic():
                obj.delete()
        except (IntegrityError, ProtectedError):
            raise ValidationError("This imported assessment is referenced by attempts and cannot be deleted.")
        return Response(status=204)



"""Scope-level compliance review APIs. Include in training/urls.py (see README)."""
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from competency.models import ProfessionalScope
from .models import (ClientPerformanceReview, ComplianceReview, ComplianceScoreHistory,
                     TrainingStaffAssignment)


def _tenant_ok(user, scope):
    return (getattr(user, 'is_superuser', False) or
            (getattr(user, 'tenant_id', None) == scope.tenant_id and scope.tenant_id is not None))


def _score(value):
    try:
        score = Decimal(str(value))
        if not score.is_finite() or score < 0 or score > 100 or score.as_tuple().exponent < -2:
            raise ValueError()
        return score
    except (InvalidOperation, ValueError, TypeError):
        return None


class ClientPerformanceReviewCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        scope = get_object_or_404(ProfessionalScope, pk=request.data.get('professional_scope'))
        if not _tenant_ok(request.user, scope):
            return Response({'success': False, 'message': 'Access denied for this scope.'}, status=403)
        rating = _score(request.data.get('rating'))
        if rating is None:
            return Response({'success': False, 'message': 'rating must be between 0 and 100 with at most two decimals.'}, status=400)
        project_id = request.data.get('project_record')
        if project_id:
            from experience.models import ProjectRecord
            if not ProjectRecord.objects.filter(pk=project_id, professional_id=scope.professional_id).exists():
                return Response({'success': False, 'message': 'Project does not belong to this professional.'}, status=400)
        review = ClientPerformanceReview.objects.create(
            tenant_id=scope.tenant_id, client=request.user, professional_scope=scope,
            project_record_id=project_id or None, rating=rating,
            feedback=request.data.get('feedback', ''),
        )
        return Response({'success': True, 'id': review.pk, 'professional_scope': scope.pk,
                         'rating': str(review.rating), 'message': 'Client review submitted; pending mentor verification.'}, status=201)


class ComplianceReviewVerifyAPIView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request, client_review_id):
        review = get_object_or_404(ClientPerformanceReview.objects.select_related('professional_scope'), pk=client_review_id)
        scope = get_object_or_404(ProfessionalScope.objects.select_for_update(), pk=review.professional_scope_id)
        if not _tenant_ok(request.user, scope):
            return Response({'success': False, 'message': 'Access denied for this scope.'}, status=403)
        # Only an assigned mentor (or platform superuser) may verify a client review.
        assigned = TrainingStaffAssignment.objects.filter(
            candidate_training__professional_scope=scope,
            mentor__user=request.user, assignment_type='MENTOR', status='ACTIVE',
        ).exists()
        if not (assigned or getattr(request.user, 'is_superuser', False)):
            return Response({'success': False, 'message': 'Only an assigned mentor may verify this review.'}, status=403)
        if review.client_id == request.user.pk:
            return Response({'success': False, 'message': 'The submitting client cannot verify their own review.'}, status=403)
        decision = str(request.data.get('status', '')).upper()
        if decision not in ('VERIFIED', 'REJECTED', 'RETURNED'):
            return Response({'success': False, 'message': 'status must be VERIFIED, REJECTED or RETURNED.'}, status=400)
        if ComplianceReview.objects.filter(client_review=review, status='VERIFIED').exists():
            return Response({'success': False, 'message': 'Review has already been verified.'}, status=409)
        score = _score(request.data.get('verified_score')) if decision == 'VERIFIED' else review.rating
        if score is None:
            return Response({'success': False, 'message': 'verified_score must be between 0 and 100 with at most two decimals.'}, status=400)
        verified = ComplianceReview.objects.create(
            tenant_id=scope.tenant_id, client_review=review, mentor=request.user,
            verified_score=score, status=decision, comments=request.data.get('comments', ''),
        )
        old_score = scope.compliance_score
        if decision == 'VERIFIED':
            scope.compliance_score = score
            scope.save(update_fields=['compliance_score', 'updated_at'])
            ComplianceScoreHistory.objects.create(
                tenant_id=scope.tenant_id, professional_scope=scope,
                compliance_review=verified, previous_score=old_score,
                new_score=score, reviewed_by=request.user,
            )
        return Response({'success': True, 'id': verified.pk, 'status': decision,
                         'professional_scope': scope.pk, 'previous_score': str(old_score),
                         'compliance_score': str(scope.compliance_score),
                         'message': 'Compliance score updated.' if decision == 'VERIFIED' else 'Review recorded; compliance score unchanged.'})



def _content_assignment_admin(request):
    """Resolve the real platform admin from DRF auth or the project's login session.

    LoginAPIView stores user_id/is_authenticated in request.session instead of
    necessarily logging the user into Django's auth middleware.
    """
    user = request.user
    if getattr(user, 'is_authenticated', False):
        return user if getattr(user, 'is_active', False) and getattr(user, 'is_superuser', False) else None

    session = request.session
    if session.get('is_authenticated') is not True:
        return None
    user_id = session.get('user_id')
    if not user_id:
        return None
    from accounts.models import UserTbl
    return UserTbl.objects.filter(pk=user_id, is_active=True, is_superuser=True, tenant__isnull=True).first()

class ContentAssignmentListCreate(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = ContentAssignment.objects.all().order_by("-created_at")
        return Response({
            "data": AssignmentSerializer(qs, many=True).data
        })

    @transaction.atomic
    def post(self, request):
        serializer = AssignmentSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        obj = serializer.save(status="ASSIGNED")

        return Response(
            AssignmentSerializer(obj).data,
            status=201
        )

class MyContentAccess(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        if not getattr(user, 'is_authenticated', False):
            session = request.session
            if session.get('is_authenticated') is not True or not session.get('user_id'):
                return Response({'detail': 'Login required.'}, status=403)
            from accounts.models import UserTbl
            user = UserTbl.objects.filter(pk=session['user_id'], is_active=True).first()
            if user is None:
                return Response({'detail': 'Login required.'}, status=403)
        qs = ContentAssignment.objects.filter(assigned_to=user, revoked_at__isnull=True, status='ASSIGNED')
        return Response({'data': AssignmentSerializer(qs, many=True).data})


class RevokeContentAssignment(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        # if _content_assignment_admin(request) is None:
        #     return Response({'detail': 'Platform administrator session required to revoke assignments.'}, status=403)
        updated = ContentAssignment.objects.filter(pk=pk, revoked_at__isnull=True).update(revoked_at=timezone.now(), status='REVOKED')
        return Response({'success': bool(updated)}, status=200 if updated else 404)
