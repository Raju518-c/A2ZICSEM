"""Shared TextChoices vocabularies reused by more than one Django app.

Enums that belong to exactly one model (e.g. Tenant.status, User.mfa_method)
are defined directly on that model instead — keep those local so a change
to one app's vocabulary can never silently affect another app.
"""

from django.db import models


class VerificationStatus(models.TextChoices):
    """Verification workflow shared by CredentialRecord, CapabilityRecord,
    ContactRecord, EmploymentRecord, ProjectRecord, ProjectScope,
    ScopeResponse, ExposureLog, EvidenceDocument and ProfessionalScope.
    """

    SELF_DECLARED = "SELF_DECLARED", "Self declared"
    EVIDENCE_UPLOADED = "EVIDENCE_UPLOADED", "Evidence uploaded"
    PENDING_REVIEW = "PENDING_REVIEW", "Pending review"
    UNDER_REVIEW = "UNDER_REVIEW", "Under review"
    VERIFIED = "VERIFIED", "Verified"
    VALIDATED = "VALIDATED", "Validated"
    REJECTED = "REJECTED", "Rejected"
    EXPIRED = "EXPIRED", "Expired"


class ResumeVisibility(models.TextChoices):
    """Controls whether a field/record may appear in a generated resume."""

    NEVER = "NEVER", "Never"
    ALWAYS = "ALWAYS", "Always"
    OPTIONAL = "OPTIONAL", "Optional"
    CLIENT_SPECIFIC = "CLIENT_SPECIFIC", "Client specific"


class DataClassification(models.TextChoices):
    """Privacy classification driving encryption, masking and audit rules."""

    PUBLIC = "PUBLIC", "Public"
    PROFESSIONAL = "PROFESSIONAL", "Professional"
    SENSITIVE_PII = "SENSITIVE_PII", "Sensitive PII"
    RESTRICTED_PII = "RESTRICTED_PII", "Restricted PII"
    COMMERCIAL = "COMMERCIAL", "Commercial"
    HEALTH = "HEALTH", "Health"


class RecordStatus(models.TextChoices):
    """DRAFT / ACTIVE / ARCHIVED lifecycle, e.g. EmploymentRecord.status."""

    DRAFT = "DRAFT", "Draft"
    ACTIVE = "ACTIVE", "Active"
    ARCHIVED = "ARCHIVED", "Archived"


class CompletionStatus(models.TextChoices):
    """DRAFT / COMPLETE / ARCHIVED lifecycle, e.g. ProjectRecord.status,
    ProjectScope.status.
    """

    DRAFT = "DRAFT", "Draft"
    COMPLETE = "COMPLETE", "Complete"
    ARCHIVED = "ARCHIVED", "Archived"


class PublicationStatus(models.TextChoices):
    """DRAFT / PUBLISHED / RETIRED lifecycle, e.g. ScopeCatalog.status,
    FormModule.status, ResumeTemplate.status.
    """

    DRAFT = "DRAFT", "Draft"
    PUBLISHED = "PUBLISHED", "Published"
    RETIRED = "RETIRED", "Retired"
