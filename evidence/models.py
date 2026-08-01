"""evidence: object-storage metadata, claim-specific evidence association,
resume import/parsing and evidence verification.

Ownership and access: Professional uploads. Tenant reviewer verifies.
Files are stored outside PostgreSQL in secure object storage — this app
only stores metadata, hashes and tenant-prefixed storage keys.
"""

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q

from core.choices import DataClassification, ResumeVisibility, VerificationStatus
from core.models import ArchivableModel, TenantOwnedModel, UUIDModel

import os
from django.utils.text import slugify


def evidence_upload_path(instance, filename):
    """
    media/tenant_name/email3+mobile3/evidence_type/filename
    """

    professional = instance.professional
    user = professional.user
    tenant = user.tenant

    tenant_name = slugify(tenant.name)

    email_part = (
        user.email.split("@")[0][:3].lower()
        if user.email
        else "usr"
    )

    mobile_part = (
        user.mobile_number[-3:]
        if user.mobile_number
        else "000"
    )

    user_folder = f"{email_part}{mobile_part}"

    evidence_type = slugify(
        str(instance.evidence_type.value)
        if hasattr(instance.evidence_type, "value")
        else str(instance.evidence_type)
    )

    return os.path.join(
        tenant_name,
        user_folder,
        evidence_type,
        filename,
    )


class EvidenceDocument(UUIDModel, TenantOwnedModel, ArchivableModel):

    class ProcessingStatus(models.TextChoices):
        UPLOADED = "UPLOADED", "Uploaded"
        SCANNING = "SCANNING", "Scanning"
        SAFE = "SAFE", "Safe"
        PARSING = "PARSING", "Parsing"
        PARSED = "PARSED", "Parsed"
        FAILED = "FAILED", "Failed"
        USER_CONFIRMED = "USER_CONFIRMED", "User Confirmed"

    professional = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.CASCADE,
        related_name="evidence_documents",
        db_index=True,
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name="evidence_documents",
    )

    object_id = models.PositiveBigIntegerField()

    target = GenericForeignKey(
        "content_type",
        "object_id",
    )

    evidence_type = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        related_name="evidence_documents",
    )

    file = models.FileField(
        upload_to=evidence_upload_path,
        max_length=1000, null=True, blank=True,
    )

    original_file_name = models.CharField(
        max_length=255,
        blank=True,
    )

    mime_type = models.CharField(
        max_length=100,
        blank=True,
    )

    file_size = models.PositiveBigIntegerField(
        null=True,
        blank=True,
    )

    issuer = models.CharField(
        max_length=200,
        blank=True,
    )

    issue_date = models.DateField(
        null=True,
        blank=True,
    )

    expiry_date = models.DateField(
        null=True,
        blank=True,
    )

    data_classification = models.CharField(
        max_length=30,
        choices=DataClassification.choices,
    )

    resume_visibility = models.CharField(
        max_length=30,
        choices=ResumeVisibility.choices,
        default=ResumeVisibility.NEVER,
    )

    verification_status = models.CharField(
        max_length=30,
        choices=VerificationStatus.choices,
        default=VerificationStatus.EVIDENCE_UPLOADED,
        db_index=True,
    )

    verified_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="evidence_documents_verified",
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    processing_status = models.CharField(
        max_length=30,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.UPLOADED,
        db_index=True,
    )

    parser_version = models.CharField(
        max_length=40,
        blank=True,
    )

    extracted_data = models.JSONField(
        default=dict,
        blank=True,
    )

    user_confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        db_table = "evidence_document"
        verbose_name = "Evidence Document"
        verbose_name_plural = "Evidence Documents"
        ordering = ["-uploaded_at"]

        constraints = [
            models.CheckConstraint(
                check=(
                    Q(issue_date__isnull=True)
                    | Q(expiry_date__isnull=True)
                    | Q(issue_date__lte=models.F("expiry_date"))
                ),
                name="chk_evidence_document_issue_before_expiry",
            ),
            models.CheckConstraint(
                check=(
                    ~Q(verification_status__in=["VERIFIED", "VALIDATED"])
                    | Q(verified_at__isnull=False)
                ),
                name="chk_evidence_document_verified_at_required",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.file:
            self.original_file_name = self.file.name.split("/")[-1]
            self.file_size = self.file.size

            if hasattr(self.file, "file"):
                self.mime_type = getattr(
                    self.file.file,
                    "content_type",
                    "",
                )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.professional} - {self.original_file_name}"
    

    