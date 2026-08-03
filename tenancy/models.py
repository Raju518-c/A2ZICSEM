"""tenancy: platform tenants, the industries/countries in which they
operate, and tenant-owned organisation structures.

Ownership and access: Platform Super Admin creates tenants and tenant
operations. Tenant Admin manages permitted organisation records within
the tenant.
"""

import os

from django.conf import settings as django_settings
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import F, Q
from django.utils.text import slugify

from core.models import TimeStampedModel, UUIDModel
from core.validators import (
    MaxFileSizeValidator,
    validate_e164_phone,
    validate_iana_timezone,
    validate_iso_country_code,
    validate_iso_currency_code,
    validate_lowercase_slug,
    validate_uppercase_code,
)

MAX_TENANT_LOGO_SIZE_BYTES = 10 * 1024 * 1024


def tenant_logo_upload_path(instance, filename):
    """
    media/tenant_name/tenant_name_docs/filename
    """

    tenant_name = slugify(instance.name)
    docs_folder = f"{tenant_name}_docs"

    return os.path.join(
        tenant_name,
        docs_folder,
        filename,
    )


class Tenant(UUIDModel, TimeStampedModel):
    """Represents each customer tenant on the shared Qualion platform and
    provides the permanent tenant portal URL.

    Key rules: Tenant code, portal slug and domain are globally unique.
    Industry and country are not uniqueness conditions. Suspended tenants
    cannot use registration or login.
    """

    class Status(models.TextChoices):
        TRIAL = "TRIAL", "Trial"
        ACTIVE = "ACTIVE", "Active"
        SUSPENDED = "SUSPENDED", "Suspended"
        CLOSED = "CLOSED", "Closed"

    name = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(2)],
        help_text="Tenant display name.",
    )
    legal_name = models.CharField(
        max_length=250,
        blank=True,
        help_text="Registered legal name, when different from display name.",
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        validators=[validate_uppercase_code],
        help_text="Stable internal tenant code.",
    )
    portal_slug = models.SlugField(
        max_length=80,
        unique=True,
        validators=[validate_lowercase_slug],
        help_text="Permanent tenant URL segment used for registration and login.",
    )
    custom_domain = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text="Optional tenant-owned domain.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
        help_text="Current tenant lifecycle status.",
    )
    registration_enabled = models.BooleanField(
        default=True,
        help_text="Registration endpoint rejects requests when false.",
    )
    login_enabled = models.BooleanField(
        default=True,
        help_text="Login endpoint rejects non-platform users when false.",
    )
    default_timezone = models.CharField(
        max_length=64,
        validators=[validate_iana_timezone],
        help_text="Default timezone used for tenant operations.",
    )
    default_currency = models.CharField(
        max_length=3,
        validators=[validate_iso_currency_code],
        help_text="Default commercial currency.",
    )
    contact_email = models.EmailField(
        max_length=254, blank=True, help_text="Primary tenant contact email."
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[validate_e164_phone],
        help_text="Primary tenant contact phone.",
    )
    settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Feature flags and non-sensitive tenant configuration.",
    )
    branding = models.JSONField(
        default=dict,
        blank=True,
        help_text="Tenant branding configuration (logo, colours, display settings).",
    )
    logo = models.ImageField(
        upload_to=tenant_logo_upload_path,
        max_length=1000,
        null=True,
        blank=True,
        validators=[MaxFileSizeValidator(MAX_TENANT_LOGO_SIZE_BYTES)],
        help_text="Tenant logo image. Max size 10MB.",
    )
    created_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        related_name="tenants_created",
        help_text="User who created the tenant. Must be the Platform Super Admin.",
    )

    class Meta:
        db_table = "tenancy_tenant"
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.contact_email:
            self.contact_email = self.contact_email.lower()
        if self.portal_slug:
            self.portal_slug = self.portal_slug.lower()
        if self.custom_domain:
            self.custom_domain = self.custom_domain.lower()
        super().save(*args, **kwargs)


class TenantOperation(TimeStampedModel):
    """Defines each Industry and Country combination in which a tenant
    operates and controls which industries are available during
    registration.

    Key rules: Only the Platform Super Admin can create or change these
    records. A tenant can have many operations across industries and
    countries.
    """

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="operations",
        db_index=True,
        help_text="Tenant that owns this operating permission.",
    )
    industry = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        related_name="tenant_operations",
        db_index=True,
        help_text="Industry in which the tenant operates. "
        "ReferenceValue.option_set must be INDUSTRY and active.",
    )
    country_code = models.CharField(
        max_length=2,
        validators=[validate_iso_country_code],
        help_text="Country of operation.",
    )
    region_name = models.CharField(
        max_length=120, blank=True, help_text="Optional state, province or region."
    )
    is_registration_enabled = models.BooleanField(
        default=True,
        help_text="Only enabled operations appear during registration.",
    )
    is_active = models.BooleanField(default=True, help_text="Operational status.")
    effective_from = models.DateField(
        null=True, blank=True, help_text="Date on which the operation becomes valid."
    )
    effective_to = models.DateField(
        null=True, blank=True, help_text="Optional end date."
    )
    created_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        related_name="tenant_operations_created",
        help_text="User who assigned the operation. Must be Platform Super Admin.",
    )

    class Meta:
        db_table = "tenancy_tenant_operation"
        verbose_name = "Tenant Operation"
        verbose_name_plural = "Tenant Operations"
        ordering = ["tenant", "industry", "country_code"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "industry", "country_code"],
                name="uniq_tenant_operation_tenant_industry_country",
            ),
            models.CheckConstraint(
                check=(
                    Q(effective_from__isnull=True)
                    | Q(effective_to__isnull=True)
                    | Q(effective_from__lte=F("effective_to"))
                ),
                name="chk_tenant_operation_effective_from_before_to",
            ),
        ]

    def __str__(self):
        return f"{self.tenant} — {self.industry} ({self.country_code})"


class Organization(UUIDModel, TimeStampedModel):
    """Stores tenant-owned branches, departments, operating units, clients,
    employers, colleges, training providers and other organisations
    referenced by professional records.

    Key rules: Parent and child must belong to the same tenant. Cycles and
    self-parenting are blocked. Users are not permanently attached to
    units; ProfessionalAssignment stores dated assignments.
    """

    class OrganizationType(models.TextChoices):
        BRANCH = "BRANCH", "Branch"
        DEPARTMENT = "DEPARTMENT", "Department"
        OPERATING_UNIT = "OPERATING_UNIT", "Operating unit"
        CLIENT = "CLIENT", "Client"
        EMPLOYER = "EMPLOYER", "Employer"
        COLLEGE = "COLLEGE", "College"
        TRAINING_PROVIDER = "TRAINING_PROVIDER", "Training provider"
        CERTIFICATION_BODY = "CERTIFICATION_BODY", "Certification body"
        VERIFICATION_AGENCY = "VERIFICATION_AGENCY", "Verification agency"
        MANUFACTURER = "MANUFACTURER", "Manufacturer"
        EPC_CONTRACTOR = "EPC_CONTRACTOR", "EPC contractor"
        SHIPYARD = "SHIPYARD", "Shipyard"
        CLASSIFICATION_SOCIETY = "CLASSIFICATION_SOCIETY", "Classification society"
        OTHER = "OTHER", "Other"

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="organizations",
        db_index=True,
        help_text="Tenant that owns the organisation record.",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
        help_text="Parent branch, department or organisation. Same tenant; "
        "cannot reference self; hierarchy cycle check required.",
    )
    organization_type = models.CharField(
        max_length=40,
        choices=OrganizationType.choices,
        help_text="Business type of the organisation.",
    )
    name = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(2)],
        help_text="Display name.",
    )
    legal_name = models.CharField(max_length=250, blank=True, help_text="Legal name.")
    code = models.CharField(
        max_length=60,
        blank=True,
        null=True,
        help_text="Tenant-specific organisation/unit code. Unique within "
        "tenant when populated.",
    )
    industry = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="organizations",
        help_text="Primary industry associated with the organisation/unit. "
        "When populated, option_set must be INDUSTRY.",
    )
    country_code = models.CharField(
        max_length=2,
        blank=True,
        validators=[validate_iso_country_code],
        help_text="Country location.",
    )
    city = models.CharField(max_length=120, blank=True, help_text="City location.")
    website = models.URLField(
        max_length=500, blank=True, help_text="Organisation website."
    )
    email = models.EmailField(
        max_length=254, blank=True, help_text="Organisation contact email."
    )
    external_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
        help_text="External system/import identifier. Unique only when the "
        "integration requires it.",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Non-sensitive organisation-specific attributes only.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive records cannot be selected for new assignments.",
    )

    class Meta:
        db_table = "tenancy_organization"
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"
        ordering = ["tenant", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "code"],
                condition=Q(code__isnull=False),
                name="uniq_organization_tenant_code",
            ),
            models.CheckConstraint(
                check=~Q(parent=F("id")),
                name="chk_organization_parent_not_self",
            ),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)
