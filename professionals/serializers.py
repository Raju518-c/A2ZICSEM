from rest_framework import serializers

from core.choices import DataClassification, ResumeVisibility
from evidence.models import EvidenceDocument

from .models import (
    CapabilityRecord,
    ContactRecord,
    CredentialRecord,
    CredentialRecordItem,
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


class Stage2SubmitSerializer(serializers.Serializer):
    """No candidate-supplied fields. Everything ProfessionalReview needs
    is derived server-side from the ProfessionalProfile itself. This
    class exists only so the endpoint has a consistent serializer_class
    attribute and can plug into extend_schema like the rest of the app.
    """
    pass


class ProfessionalReviewDecisionSerializer(serializers.Serializer):
    """Input for a reviewer deciding on a submitted ProfessionalReview.
    Mirrors RegistrationApplicationDecisionSerializer's shape exactly.
    """

    decision = serializers.ChoiceField(choices=["APPROVED", "REJECTED", "RETURNED"])
    final_classification = serializers.ChoiceField(
        choices=["CANDIDATE", "MENTOR"],
        required=False,
        allow_blank=True,
        help_text="Required when decision=APPROVED — DB constraint enforces this.",
    )
    reviewed_by = serializers.CharField(
        required=False, allow_blank=True, allow_null=True,
        help_text="UserTbl id or public_id of the reviewing Tenant Admin/Reviewer.",
    )
    reason = serializers.CharField(
        required=False, allow_blank=True,
        help_text="Required when decision=REJECTED or RETURNED.",
    )
    reviewer_notes = serializers.CharField(required=False, allow_blank=True)


class ProfessionalReviewResubmitSerializer(serializers.Serializer):
    """No fields needed — resubmission just re-triggers the completeness
    check and creates a fresh ProfessionalReview row against whatever
    Stage 2 data the candidate has since corrected via the section POSTs.
    """
    pass


class CredentialRecordItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = CredentialRecordItem
        fields = "__all__"
        
class CredentialRecordSerializer(serializers.ModelSerializer):
    items = CredentialRecordItemSerializer(many=True, read_only=True)
    class Meta:
        model = CredentialRecord
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class CapabilityRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapabilityRecord
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, attrs):
        def current(field, default=""):
            return attrs.get(field, getattr(self.instance, field, default))

        capability_type = current("capability_type", None)
        reference_value = current("reference_value", None)
        custom_name = current("custom_name")
        speaking_level = current("speaking_level")
        reading_level = current("reading_level")
        writing_level = current("writing_level")

        if not reference_value and not custom_name:
            raise serializers.ValidationError(
                {"custom_name": "custom_name is required when reference_value is not set."}
            )

        if capability_type == "LANGUAGE" and not (speaking_level and reading_level and writing_level):
            raise serializers.ValidationError(
                {"speaking_level": "speaking_level, reading_level and writing_level are all required when capability_type=LANGUAGE."}
            )

        return attrs



class ContactRecordSerializer(serializers.ModelSerializer):
    resume_visibility = serializers.ChoiceField(
        choices=ResumeVisibility.choices, required=False
    )
    data_classification = serializers.ChoiceField(
        choices=DataClassification.choices, required=False
    )

    class Meta:
        model = ContactRecord
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    # Defaults documented on the model's help_text: reference contacts default
    # to CLIENT_SPECIFIC/SENSITIVE_PII, emergency contacts to NEVER/RESTRICTED_PII.
    _CONTACT_TYPE_DEFAULTS = {
        ContactRecord.ContactType.PROFESSIONAL_REFERENCE: {
            "resume_visibility": ResumeVisibility.CLIENT_SPECIFIC,
            "data_classification": DataClassification.SENSITIVE_PII,
        },
        ContactRecord.ContactType.EMERGENCY_CONTACT: {
            "resume_visibility": ResumeVisibility.NEVER,
            "data_classification": DataClassification.RESTRICTED_PII,
        },
    }

    def validate(self, attrs):
        if self.instance is None:  # only auto-fill on create; never override an existing record's values
            defaults = self._CONTACT_TYPE_DEFAULTS.get(attrs.get("contact_type"), {})
            for field, value in defaults.items():
                attrs.setdefault(field, value)
        return attrs
    
    
class CombinedCredentialRecordItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = CredentialRecordItem
        fields = "__all__"
        read_only_fields = ("credential_record", "tenant")


class CombinedCredentialRecordSerializer(serializers.ModelSerializer):
    items = CombinedCredentialRecordItemSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = CredentialRecord
        fields = "__all__"
        read_only_fields = (
            "created_at",
            "updated_at"
        )

    def create(self, validated_data):
        print("validated_data =", validated_data)

        items_data = validated_data.pop("items", [])
        tenant = validated_data.pop("tenant")

        credential = CredentialRecord.objects.create(
            tenant=tenant,
            **validated_data
        )

        for item_data in items_data:
            CredentialRecordItem.objects.create(
                credential_record=credential,
                tenant=tenant,
                **item_data
            )

        return credential

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)

        # --------------------------------
        # Update Parent Record
        # --------------------------------
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # --------------------------------
        # Update Child Items
        # --------------------------------
        if items_data is not None:

            existing_items = {
                item.id: item
                for item in instance.items.all()
            }

            received_item_ids = []

            for item_data in items_data:

                item_id = item_data.get("id")

                # --------------------------
                # Update Existing Item
                # --------------------------
                if item_id and item_id in existing_items:

                    item = existing_items[item_id]

                    for key, value in item_data.items():
                        if key != "id":
                            setattr(item, key, value)

                    item.save()

                    received_item_ids.append(item_id)

                # --------------------------
                # Create New Item
                # --------------------------
                else:

                    CredentialRecordItem.objects.create(
                        credential_record=instance,
                        **item_data
                    )

            # --------------------------------
            # Delete Removed Items
            # --------------------------------
            for item_id, obj in existing_items.items():
                if item_id not in received_item_ids:
                    obj.delete()

        return instance




