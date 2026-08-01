from rest_framework import serializers
from .models import *


class ProfessionalScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalScope
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )








class CompetencyAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetencyAssessment
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
        )