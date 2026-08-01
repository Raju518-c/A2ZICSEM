from rest_framework import serializers
from .models import *


class ResumeTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeTemplate
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )






class ResumeGenerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeGeneration
        fields = "__all__"
        read_only_fields = (
            "id",
            "generated_at",
        )