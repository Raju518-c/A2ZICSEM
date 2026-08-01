from rest_framework import serializers

from evidence.models import EvidenceDocument

from .models import (
    CapabilityRecord,
    ContactRecord,
    CredentialRecord,
    ProfessionalProfile,
    ProfessionalReview,
)


class ProfessionalProfileSerializer(serializers.ModelSerializer):
    profile_photo_evidence = serializers.PrimaryKeyRelatedField(
        queryset=EvidenceDocument.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ProfessionalProfile
        fields = "__all__"
        read_only_fields = ["public_id", "created_at", "updated_at"]


class ProfessionalReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalReview
        fields = "__all__"
        read_only_fields = ["created_at"]


class CredentialRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CredentialRecord
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class CapabilityRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapabilityRecord
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class ContactRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactRecord
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
