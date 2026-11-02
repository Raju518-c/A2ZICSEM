from rest_framework import serializers
from .models import EcosystemMember


class EcosystemMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = EcosystemMember
        fields = "__all__"
        read_only_fields = (
            "id",
            "joined_at",
            "updated_at",
        )

    def validate_email(self, value):
        email = value.strip().lower()

        queryset = EcosystemMember.objects.filter(
            email__iexact=email
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "This email is already registered in Join Ecosystem."
            )

        return email