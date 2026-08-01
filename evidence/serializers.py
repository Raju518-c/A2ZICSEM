from rest_framework import serializers
from .models import *


class EvidenceDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenceDocument
        fields = "__all__"
        read_only_fields = (
            "id",
            "uploaded_at",
            "original_file_name",
            "file_size",
            "mime_type",
        )