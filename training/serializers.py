# training/combined_serializers.py

from django.db import transaction
from rest_framework import serializers
from .models import *


# 1. TrainingProgram + multiple TrainingModule

class TrainingModuleNestedSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = TrainingModule
        fields = (
            "id", "code", "title", "description", "content_type",
            "content_storage_key", "content_url", "sequence",
            "duration_minutes", "is_mandatory", "is_active",
        )


class TrainingProgramWithModulesSerializer(serializers.ModelSerializer):
    modules = TrainingModuleNestedSerializer(many=True, required=False)

    class Meta:
        model = TrainingProgram
        fields = (
            "id", "code", "name", "description", "scope",
            "target_qualion_level", "version", "estimated_duration_hours",
            "status", "created_by", "published_at", "modules",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    @transaction.atomic
    def create(self, validated_data):
        modules_data = validated_data.pop("modules", [])
        program = TrainingProgram.objects.create(**validated_data)
        for module_data in modules_data:
            module_data.pop("id", None)
            TrainingModule.objects.create(program=program, **module_data)
        return program

    @transaction.atomic
    def update(self, instance, validated_data):
        modules_data = validated_data.pop("modules", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.full_clean()
        instance.save()

        # If modules is omitted, leave current modules unchanged.
        # If supplied, update by id, create without id, and delete omitted
        # modules only if the client explicitly sends "replace_modules": true
        # is not supported by this serializer. Existing omitted modules remain.
        if modules_data is not None:
            for module_data in modules_data:
                module_id = module_data.pop("id", None)
                if module_id:
                    module = TrainingModule.objects.get(
                        pk=module_id, program=instance
                    )
                    for attr, value in module_data.items():
                        setattr(module, attr, value)
                    module.full_clean()
                    module.save()
                else:
                    TrainingModule.objects.create(
                        program=instance, **module_data
                    )
        return instance


# 2. One or multiple QuestionBank records + options for each question

class QuestionOptionNestedSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = QuestionOption
        fields = ("id", "option_text", "sequence", "is_correct", "created_at", "updated_at")
        read_only_fields = ("created_at", "updated_at")


class QuestionBankWithOptionsSerializer(serializers.ModelSerializer):
    options = QuestionOptionNestedSerializer(many=True, required=False)

    class Meta:
        model = QuestionBank
        fields = (
            "id", "scope", "qualion_level", "question_text", "difficulty",
            "explanation", "marks", "version", "status", "created_by",
            "options", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    @transaction.atomic
    def create(self, validated_data):
        options_data = validated_data.pop("options", [])
        question = QuestionBank.objects.create(**validated_data)
        for option_data in options_data:
            option_data.pop("id", None)
            QuestionOption.objects.create(question=question, **option_data)
        return question

    @transaction.atomic
    def update(self, instance, validated_data):
        options_data = validated_data.pop("options", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.full_clean()
        instance.save()

        if options_data is not None:
            for option_data in options_data:
                option_id = option_data.pop("id", None)
                if option_id:
                    option = QuestionOption.objects.get(
                        pk=option_id, question=instance
                    )
                    for attr, value in option_data.items():
                        setattr(option, attr, value)
                    option.full_clean()
                    option.save()
                else:
                    QuestionOption.objects.create(
                        question=instance, **option_data
                    )
        return instance


# 3. One TrainingAssessment + multiple AssessmentQuestionConfig

class AssessmentQuestionConfigNestedSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = AssessmentQuestionConfig
        fields = (
            "id", "difficulty", "question_count", "marks_per_question",
            "created_at", "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")


class TrainingAssessmentWithConfigsSerializer(serializers.ModelSerializer):
    question_configs = AssessmentQuestionConfigNestedSerializer(
        many=True, required=False
    )

    class Meta:
        model = TrainingAssessment
        fields = (
            "id", "program", "code", "title", "duration_minutes",
            "passing_percentage", "max_attempts", "status",
            "question_configs", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    @transaction.atomic
    def create(self, validated_data):
        configs_data = validated_data.pop("question_configs", [])
        assessment = TrainingAssessment.objects.create(**validated_data)
        for config_data in configs_data:
            config_data.pop("id", None)
            AssessmentQuestionConfig.objects.create(
                assessment=assessment, **config_data
            )
        return assessment

    @transaction.atomic
    def update(self, instance, validated_data):
        configs_data = validated_data.pop("question_configs", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.full_clean()
        instance.save()

        if configs_data is not None:
            for config_data in configs_data:
                config_id = config_data.pop("id", None)
                if config_id:
                    config = AssessmentQuestionConfig.objects.get(
                        pk=config_id, assessment=instance
                    )
                    for attr, value in config_data.items():
                        setattr(config, attr, value)
                    config.full_clean()
                    config.save()
                else:
                    AssessmentQuestionConfig.objects.create(
                        assessment=instance, **config_data
                    )
        return instance


# 4. TenantTrainingProgram (single or multiple)
# The API view supplies tenant and imported_by from the authenticated context.

class TenantTrainingProgramItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantTrainingProgram
        fields = (
            "id", "master_program", "imported_version", "imported_by",
            "is_active", "created_at", "updated_at",
        )
        read_only_fields = ("id", "imported_by", "created_at", "updated_at")

    def validate(self, attrs):
        master_program = attrs.get(
            "master_program",
            getattr(self.instance, "master_program", None),
        )
        if master_program and master_program.status != "PUBLISHED":
            raise serializers.ValidationError(
                {"master_program": "Only PUBLISHED programs can be imported."}
            )
        return attrs


class TenantTrainingProgramBulkSerializer(serializers.Serializer):
    # Accept either one object or {"items": [ ... ]} in the view.
    items = TenantTrainingProgramItemSerializer(many=True)


# 5. TenantAssessment (single or multiple)
# The API view supplies tenant and imported_by from the authenticated context.

class TenantAssessmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantAssessment
        fields = (
            "id", "tenant_program", "master_assessment", "imported_by",
            "is_active", "created_at", "updated_at",
        )
        read_only_fields = ("id", "imported_by", "created_at", "updated_at")

    def validate(self, attrs):
        tenant_program = attrs.get(
            "tenant_program",
            getattr(self.instance, "tenant_program", None),
        )
        master_assessment = attrs.get(
            "master_assessment",
            getattr(self.instance, "master_assessment", None),
        )
        if master_assessment and master_assessment.status != "PUBLISHED":
            raise serializers.ValidationError(
                {"master_assessment": "Only PUBLISHED assessments can be imported."}
            )
        if tenant_program and master_assessment:
            if tenant_program.master_program_id != master_assessment.program_id:
                raise serializers.ValidationError(
                    "The assessment must belong to the tenant program's master program."
                )
        return attrs


class TenantAssessmentBulkSerializer(serializers.Serializer):
    items = TenantAssessmentItemSerializer(many=True)



class QuestionFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
        fields = (
            "id", "scope", "qualion_level", "question_text", "difficulty",
            "explanation", "marks", "version", "status", "created_by",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class QuestionOptionFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ("id", "option_text", "sequence", "is_correct", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class QuestionOptionUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = QuestionOption
        fields = ("id", "option_text", "sequence", "is_correct")
        extra_kwargs = {
            "option_text": {"required": False},
            "sequence": {"required": False},
            "is_correct": {"required": False},
        }


class QuestionReadSerializer(serializers.ModelSerializer):
    Options = QuestionOptionFieldsSerializer(source="options", many=True, read_only=True)

    class Meta:
        model = QuestionBank
        fields = (
            "id", "scope", "qualion_level", "question_text", "difficulty",
            "explanation", "marks", "version", "status", "created_by",
            "created_at", "updated_at", "Options",
        )


class AssessmentFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingAssessment
        fields = (
            "id", "program", "code", "title", "duration_minutes",
            "passing_percentage", "max_attempts", "status", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class AssessmentConfigFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentQuestionConfig
        fields = ("id", "difficulty", "question_count", "marks_per_question", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class AssessmentConfigUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = AssessmentQuestionConfig
        fields = ("id", "difficulty", "question_count", "marks_per_question")
        extra_kwargs = {
            "difficulty": {"required": False},
            "question_count": {"required": False},
            "marks_per_question": {"required": False},
        }


class AssessmentReadSerializer(serializers.ModelSerializer):
    Configs = AssessmentConfigFieldsSerializer(source="question_configs", many=True, read_only=True)

    class Meta:
        model = TrainingAssessment
        fields = (
            "id", "program", "code", "title", "duration_minutes",
            "passing_percentage", "max_attempts", "status", "created_at", "updated_at", "Configs",
        )


class TenantTrainingProgramFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantTrainingProgram
        fields = ("id", "master_program", "imported_version", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_master_program(self, value):
        if value.status != "PUBLISHED":
            raise serializers.ValidationError("Only PUBLISHED programs can be imported.")
        return value


class TenantAssessmentFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantAssessment
        fields = ("id", "tenant_program", "master_assessment", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        tenant_program = attrs.get("tenant_program", getattr(self.instance, "tenant_program", None))
        master_assessment = attrs.get("master_assessment", getattr(self.instance, "master_assessment", None))
        if master_assessment and master_assessment.status != "PUBLISHED":
            raise serializers.ValidationError({"master_assessment": "Only PUBLISHED assessments can be imported."})
        if tenant_program and master_assessment and tenant_program.master_program_id != master_assessment.program_id:
            raise serializers.ValidationError("Assessment must belong to the tenant program's master program.")
        return attrs



class TrainingProgramFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingProgram
        fields = (
            "id", "code", "name", "description", "scope",
            "target_qualion_level", "version", "estimated_duration_hours",
            "status", "created_by", "published_at", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class TrainingModuleFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingModule
        fields = (
            "id", "code", "title", "description", "content_type",
            "content_storage_key", "content_url", "sequence",
            "duration_minutes", "is_mandatory", "is_active",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class TrainingModuleUpdateItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = TrainingModule
        fields = (
            "id", "code", "title", "description", "content_type",
            "content_storage_key", "content_url", "sequence",
            "duration_minutes", "is_mandatory", "is_active",
        )
        extra_kwargs = {
            "code": {"required": False},
            "title": {"required": False},
            "description": {"required": False},
            "content_type": {"required": False},
            "content_storage_key": {"required": False},
            "content_url": {"required": False},
            "sequence": {"required": False},
            "duration_minutes": {"required": False},
            "is_mandatory": {"required": False},
            "is_active": {"required": False},
        }


class TrainingProgramWithModulesReadSerializer(serializers.ModelSerializer):
    Modules = TrainingModuleFieldsSerializer(source="modules", many=True, read_only=True)

    class Meta:
        model = TrainingProgram
        fields = (
            "id", "code", "name", "description", "scope",
            "target_qualion_level", "version", "estimated_duration_hours",
            "status", "created_by", "published_at", "created_at", "updated_at",
            "Modules",
        )

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import *

class AssignmentSerializer(serializers.ModelSerializer):
    assigned_by = serializers.PrimaryKeyRelatedField(
        queryset=UserTbl.objects.filter(
            is_active=True            
        ),
        required=True
    )

    class Meta:
        model = ContentAssignment
        fields = [
            "id", "assigned_to", "assigned_by",
            "content_type", "target_type",
            "industries", "scopes",
            "can_create", "can_edit", "can_submit",
            "due_date", "status", "notes", "revoked_at"
        ]
        read_only_fields = ["id", "revoked_at"]