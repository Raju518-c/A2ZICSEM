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



class ResumeBuilderSerializer(serializers.Serializer):

    professional_profile_id = serializers.IntegerField()

    template = serializers.JSONField(
        allow_null=True
    )

    header = serializers.JSONField()

    personal_details = serializers.JSONField()

    profile = serializers.JSONField()

    education = serializers.ListField()

    certifications = serializers.ListField()

    training = serializers.ListField()

    employment = serializers.ListField()

    projects = serializers.ListField()

    scope_expertise = serializers.ListField()

    skills = serializers.JSONField()

    languages = serializers.ListField()

    references = serializers.JSONField()

    client_approvals = serializers.ListField()

    declaration = serializers.JSONField(
        allow_null=True
    )

    meta = serializers.JSONField()