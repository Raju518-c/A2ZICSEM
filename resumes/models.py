"""resumes: versioned client resume templates and immutable generated
resume records built from Stage 1/Stage 2/profile evidence.

Ownership and access: Tenant Admin configures client-specific templates
using approved source tokens. Professional and reviewer generate/approve
outputs according to permissions.
"""
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models
from django.db.models import F, Q

from core.choices import PublicationStatus
from core.models import TenantOwnedModel, TimeStampedModel, UUIDModel


class ResumeTemplate(TenantOwnedModel, TimeStampedModel):
    """Stores one versioned client resume layout and its field mapping,
    required-field and confidentiality configuration.

    Key rules: Published versions are immutable. Mapping cannot bypass
    privacy classification or consent. Changes create a new template
    version.
    """

    class OutputType(models.TextChoices):
        PDF = "PDF", "PDF"
        DOCX = "DOCX", "DOCX"
        HTML = "HTML", "HTML"

    client_organization = models.ForeignKey(
        "tenancy.Organization",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="resume_templates",
        help_text="Client that owns/requests the format. Same tenant; "
        "CLIENT type recommended.",
    )
    template_code = models.CharField(
        max_length=60,
        help_text="Stable template code; unique within tenant and client with version.",
    )
    template_name = models.CharField(max_length=180, help_text="Template display name.")
    version = models.CharField(
        max_length=30, help_text="Template version; versioned publication process."
    )
    output_type = models.CharField(
        max_length=20, choices=OutputType.choices, help_text="Generated file format."
    )
    template_storage_key = models.CharField(
        max_length=600, blank=True, help_text="Uploaded source template file "
        "(tenant-prefixed object-storage key)."
    )
    mapping_schema = models.JSONField(
        default=dict,
        blank=True,
        help_text="Field-to-template mapping configuration: sections, source "
        "tokens, transforms, repeat and display rules.",
    )
    required_fields_schema = models.JSONField(
        default=dict,
        blank=True,
        help_text="Template completeness requirements: mandatory mappings "
        "and gap questions.",
    )
    confidentiality_rules = models.JSONField(
        default=dict,
        blank=True,
        help_text="Masking and sensitive-data rules; cannot permit restricted "
        "fields without explicit approved rule and consent.",
    )
    status = models.CharField(
        max_length=20,
        choices=PublicationStatus.choices,
        default=PublicationStatus.DRAFT,
        db_index=True,
        help_text="Publication status.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Availability status; only active published templates can "
        "create final outputs.",
    )
    created_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        related_name="resume_templates_created",
        help_text="Template creator; same-tenant Tenant Admin or authorised "
        "template manager.",
    )
    published_at = models.DateTimeField(
        null=True, blank=True, help_text="Publication timestamp; required when PUBLISHED."
    )
    retired_at = models.DateTimeField(
        null=True, blank=True, help_text="Retirement timestamp; required when retired."
    )

    class Meta:
        db_table = "resumes_resume_template"
        verbose_name = "Resume Template"
        verbose_name_plural = "Resume Templates"
        ordering = ["template_code", "version"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "client_organization", "template_code", "version"],
                name="uniq_resume_template_tenant_client_code_version",
            ),
            models.CheckConstraint(
                check=(~Q(status="PUBLISHED") | Q(published_at__isnull=False)),
                name="chk_resume_template_published_at_required",
            ),
            models.CheckConstraint(
                check=(~Q(status="RETIRED") | Q(retired_at__isnull=False)),
                name="chk_resume_template_retired_at_required",
            ),
        ]

    def __str__(self):
        return f"{self.template_code} v{self.version}"


class ResumeGeneration(UUIDModel, TenantOwnedModel):
    """Immutable record of each generated or submitted resume, including
    the exact source data, consent and validation snapshot.

    Key rules: Submitted outputs are never overwritten or deleted. Profile
    changes create a new generation. Mandatory gaps and restricted-field
    failures block approval/submission.
    """

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PENDING_REVIEW = "PENDING_REVIEW", "Pending review"
        APPROVED = "APPROVED", "Approved"
        SUBMITTED = "SUBMITTED", "Submitted"
        SUPERSEDED = "SUPERSEDED", "Superseded"
        CANCELLED = "CANCELLED", "Cancelled"

    professional = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.PROTECT,
        related_name="resume_generations",
        db_index=True,
        help_text="Professional whose resume is generated.",
    )
    resume_template = models.ForeignKey(
        ResumeTemplate,
        on_delete=models.PROTECT,
        related_name="generations",
        help_text="Template version used; same tenant, published for final output.",
    )
    generated_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        related_name="resume_generations_created",
        help_text="User who triggered generation; same tenant, must have permission.",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        help_text="Generation workflow status.",
    )
    source_snapshot = models.JSONField(
        help_text="Source data used for the output; immutable after "
        "generation; sensitive values masked/encrypted as required."
    )
    override_values = models.JSONField(
        default=dict,
        blank=True,
        help_text="Output-only approved overrides; only template fields "
        "marked user-overridable; never changes core profile.",
    )
    consent_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="Consent state used for generation: applicable consent/"
        "declaration versions and timestamps.",
    )
    validation_result = models.JSONField(
        default=dict,
        blank=True,
        help_text="Template readiness validation: missing, unverified, "
        "confidential and restricted-field results.",
    )
    output_storage_key = models.CharField(
        max_length=600, blank=True, help_text="Generated resume file location "
        "(tenant-prefixed object-storage key)."
    )
    output_hash = models.CharField(
        max_length=128, blank=True, help_text="Generated file integrity hash "
        "(SHA-256 or stronger)."
    )
    reviewed_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="resume_generations_reviewed",
        help_text="Reviewer; same-tenant authorised reviewer.",
    )
    reviewed_at = models.DateTimeField(
        null=True, blank=True, help_text="Required for approved review state."
    )
    submitted_at = models.DateTimeField(
        null=True, blank=True, help_text="Required when status=SUBMITTED."
    )
    supersedes = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="superseded_by",
        help_text="Prior resume generation replaced by this one. Same "
        "professional/tenant; cannot form cycle.",
    )
    generated_at = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text="Generation timestamp."
    )

    class Meta:
        db_table = "resumes_resume_generation"
        verbose_name = "Resume Generation"
        verbose_name_plural = "Resume Generations"
        ordering = ["-generated_at"]
        constraints = [
            models.CheckConstraint(
                check=(~Q(status="APPROVED") | Q(reviewed_at__isnull=False)),
                name="chk_resume_generation_reviewed_at_required",
            ),
            models.CheckConstraint(
                check=(~Q(status="SUBMITTED") | Q(submitted_at__isnull=False)),
                name="chk_resume_generation_submitted_at_required",
            ),            
        ]
        
    def clean(self):
        super().clean()

        if self.supersedes_id and self.supersedes_id == self.id:
            raise ValidationError({
                "supersedes": "Resume generation cannot supersede itself."
            })        

    def __str__(self):
        return f"{self.professional} — {self.resume_template} ({self.status})"
