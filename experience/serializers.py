from rest_framework import serializers
from .models import *


class EmploymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmploymentRecord
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )






class ProjectRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectRecord
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )





class ProjectScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectScope
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )







class ScopeResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScopeResponse
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )



class ExposureLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExposureLog
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )





class ProfessionalAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalAssignment
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )