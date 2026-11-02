from django.db import models


class EcosystemMember(models.Model):

    class Role(models.TextChoices):
        GRADUATE = "GRADUATE", "Graduate"
        SURVEYOR = "SURVEYOR", "Surveyor"
        MENTOR = "MENTOR", "Mentor"
        INSPECTION_COMPANY = "INSPECTION_COMPANY", "Inspection Company"
        EPC_CONTRACTOR = "EPC_CONTRACTOR", "EPC Contractor"
        MANUFACTURER = "MANUFACTURER", "Manufacturer"

    id = models.AutoField(primary_key=True)

    full_name = models.CharField(max_length=200)

    email = models.EmailField(
        unique=True,
        db_index=True
    )

    organisation = models.CharField(
        max_length=255,
        blank=True
    )

    role = models.CharField(
        max_length=30,
        choices=Role.choices
    )

    message = models.TextField(blank=True)

    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecosystem_member"

    def __str__(self):
        return f"{self.full_name} - {self.get_role_display()}"