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
from django.core.exceptions import ValidationError
from core.choices import VerificationStatus
from core.fields import EncryptedCharField
from core.models import ArchivableModel, CreatedOnlyModel, TenantOwnedModel, TimeStampedModel, UUIDModel
from core.validators import (
    MaxFileSizeValidator,
    validate_e164_phone,
    validate_iana_timezone, validate_iso_country_code, validate_iso_currency_code, validate_lowercase_slug, validate_uppercase_code,
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


# class Tenant(UUIDModel, TimeStampedModel):
#     """Represents each customer tenant on the shared Qualion platform and
#     provides the permanent tenant portal URL.

#     Key rules: Tenant code, portal slug and domain are globally unique.
#     Industry and country are not uniqueness conditions. Suspended tenants
#     cannot use registration or login.
#     """

#     class Status(models.TextChoices):
#         TRIAL = "TRIAL", "Trial"
#         ACTIVE = "ACTIVE", "Active"
#         SUSPENDED = "SUSPENDED", "Suspended"
#         CLOSED = "CLOSED", "Closed"

#     name = models.CharField(
#         max_length=200,
#         validators=[MinLengthValidator(2)],
#         help_text="Tenant display name.",
#     )
#     legal_name = models.CharField(
#         max_length=250,
#         blank=True,
#         help_text="Registered legal name, when different from display name.",
#     )
#     code = models.CharField(
#         max_length=50,
#         unique=True,
#         validators=[validate_uppercase_code],
#         help_text="Stable internal tenant code.",
#     )
#     portal_slug = models.SlugField(
#         max_length=80,
#         unique=True,
#         validators=[validate_lowercase_slug],
#         help_text="Permanent tenant URL segment used for registration and login.",
#     )
#     custom_domain = models.CharField(
#         max_length=255,
#         unique=True,
#         null=True,
#         blank=True,
#         help_text="Optional tenant-owned domain.",
#     )
#     status = models.CharField(
#         max_length=20,
#         choices=Status.choices,
#         default=Status.ACTIVE,
#         db_index=True,
#         help_text="Current tenant lifecycle status.",
#     )
#     registration_enabled = models.BooleanField(
#         default=True,
#         help_text="Registration endpoint rejects requests when false.",
#     )
#     login_enabled = models.BooleanField(
#         default=True,
#         help_text="Login endpoint rejects non-platform users when false.",
#     )
#     default_timezone = models.CharField(
#         max_length=64,
#         validators=[validate_iana_timezone],
#         help_text="Default timezone used for tenant operations.",
#     )
#     default_currency = models.CharField(
#         max_length=3,
#         validators=[validate_iso_currency_code],
#         help_text="Default commercial currency.",
#     )
#     contact_email = models.EmailField(
#         max_length=254, blank=True, help_text="Primary tenant contact email."
#     )
#     contact_phone = models.CharField(
#         max_length=20,
#         blank=True,
#         validators=[validate_e164_phone],
#         help_text="Primary tenant contact phone.",
#     )
#     settings = models.JSONField(
#         default=dict,
#         blank=True,
#         help_text="Feature flags and non-sensitive tenant configuration.",
#     )
#     branding = models.JSONField(
#         default=dict,
#         blank=True,
#         help_text="Tenant branding configuration (logo, colours, display settings).",
#     )
#     logo = models.ImageField(
#         upload_to=tenant_logo_upload_path,
#         max_length=1000,
#         null=True,
#         blank=True,
#         validators=[MaxFileSizeValidator(MAX_TENANT_LOGO_SIZE_BYTES)],
#         help_text="Tenant logo image. Max size 10MB.",
#     )
#     created_by = models.ForeignKey(
#         "accounts.UserTbl",
#         on_delete=models.PROTECT,
#         related_name="tenants_created",
#         help_text="User who created the tenant. Must be the Platform Super Admin.",
#     )

#     class Meta:
#         db_table = "tenancy_tenant"
#         verbose_name = "Tenant"
#         verbose_name_plural = "Tenant"
#         ordering = ["name"]

#     def __str__(self):
#         return self.name

#     def save(self, *args, **kwargs):
#         if self.contact_email:
#             self.contact_email = self.contact_email.lower()
#         if self.portal_slug:
#             self.portal_slug = self.portal_slug.lower()
#         if self.custom_domain:
#             self.custom_domain = self.custom_domain.lower()
#         super().save(*args, **kwargs)


# class TenantOperation(TimeStampedModel):
#     """Defines each Industry and Country combination in which a tenant
#     operates and controls which industries are available during
#     registration.

#     Key rules: Only the Platform Super Admin can create or change these
#     records. A tenant can have many operations across industries and
#     countries.
#     """

#     tenant = models.ForeignKey(
#         Tenant,
#         on_delete=models.CASCADE,
#         related_name="operations",
#         db_index=True,
#         help_text="Tenant that owns this operating permission.",
#     )
#     industry = models.ForeignKey(
#         "catalog.ReferenceValue",
#         on_delete=models.PROTECT,
#         related_name="tenant_operations",
#         db_index=True,
#         help_text="Industry in which the tenant operates. "
#         "ReferenceValue.option_set must be INDUSTRY and active.",
#     )
#     country_code = models.CharField(
#         max_length=2,
#         validators=[validate_iso_country_code],
#         help_text="Country of operation.",
#     )
#     region_name = models.CharField(
#         max_length=120, blank=True, help_text="Optional state, province or region."
#     )
#     is_registration_enabled = models.BooleanField(
#         default=True,
#         help_text="Only enabled operations appear during registration.",
#     )
#     is_active = models.BooleanField(default=True, help_text="Operational status.")
#     effective_from = models.DateField(
#         null=True, blank=True, help_text="Date on which the operation becomes valid."
#     )
#     effective_to = models.DateField(
#         null=True, blank=True, help_text="Optional end date."
#     )
#     created_by = models.ForeignKey(
#         "accounts.UserTbl",
#         on_delete=models.PROTECT,
#         related_name="tenant_operations_created",
#         help_text="User who assigned the operation. Must be Platform Super Admin.",
#     )

#     class Meta:
#         db_table = "tenancy_tenant_operation"
#         verbose_name = "TenantOperation"
#         verbose_name_plural = "TenantOperation"
#         ordering = ["tenant", "industry", "country_code"]
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["tenant", "industry", "country_code"],
#                 name="uniq_tenant_operation_tenant_industry_country",
#             ),
#             models.CheckConstraint(
#                 check=(
#                     Q(effective_from__isnull=True)
#                     | Q(effective_to__isnull=True)
#                     | Q(effective_from__lte=F("effective_to"))
#                 ),
#                 name="chk_tenant_operation_effective_from_before_to",
#             ),
#         ]

#     def __str__(self):
#         return f"{self.tenant} — {self.industry} ({self.country_code})"


# class Organization(UUIDModel, TimeStampedModel):
#     """Stores tenant-owned branches, departments, operating units, clients,
#     employers, colleges, training providers and other organisations
#     referenced by professional records.

#     Key rules: Parent and child must belong to the same tenant. Cycles and
#     self-parenting are blocked. Users are not permanently attached to
#     units; ProfessionalAssignment stores dated assignments.
#     """

#     class OrganizationType(models.TextChoices):
#         BRANCH = "BRANCH", "Branch"
#         DEPARTMENT = "DEPARTMENT", "Department"
#         OPERATING_UNIT = "OPERATING_UNIT", "Operating unit"
#         CLIENT = "CLIENT", "Client"
#         EMPLOYER = "EMPLOYER", "Employer"
#         COLLEGE = "COLLEGE", "College"
#         TRAINING_PROVIDER = "TRAINING_PROVIDER", "Training provider"
#         CERTIFICATION_BODY = "CERTIFICATION_BODY", "Certification body"
#         VERIFICATION_AGENCY = "VERIFICATION_AGENCY", "Verification agency"
#         MANUFACTURER = "MANUFACTURER", "Manufacturer"
#         EPC_CONTRACTOR = "EPC_CONTRACTOR", "EPC contractor"
#         SHIPYARD = "SHIPYARD", "Shipyard"
#         CLASSIFICATION_SOCIETY = "CLASSIFICATION_SOCIETY", "Classification society"
#         OTHER = "OTHER", "Other"

#     tenant = models.ForeignKey(
#         Tenant,
#         on_delete=models.CASCADE,
#         related_name="organizations",
#         db_index=True,
#         help_text="Tenant that owns the organisation record.",
#     )
#     parent = models.ForeignKey(
#         "self",
#         on_delete=models.PROTECT,
#         null=True,
#         blank=True,
#         related_name="children",
#         help_text="Parent branch, department or organisation. Same tenant; "
#         "cannot reference self; hierarchy cycle check required.",
#     )
#     organization_type = models.CharField(
#         max_length=40,
#         choices=OrganizationType.choices,
#         help_text="Business type of the organisation.",
#     )
#     name = models.CharField(
#         max_length=200,
#         validators=[MinLengthValidator(2)],
#         help_text="Display name.",
#     )
#     legal_name = models.CharField(max_length=250, blank=True, help_text="Legal name.")
#     code = models.CharField(
#         max_length=60,
#         blank=True,
#         null=True,
#         help_text="Tenant-specific organisation/unit code. Unique within "
#         "tenant when populated.",
#     )
#     industry = models.ForeignKey(
#         "catalog.ReferenceValue",
#         on_delete=models.PROTECT,
#         null=True,
#         blank=True,
#         related_name="organizations",
#         help_text="Primary industry associated with the organisation/unit. "
#         "When populated, option_set must be INDUSTRY.",
#     )
#     country_code = models.CharField(
#         max_length=2,
#         blank=True,
#         validators=[validate_iso_country_code],
#         help_text="Country location.",
#     )
#     city = models.CharField(max_length=120, blank=True, help_text="City location.")
#     website = models.URLField(
#         max_length=500, blank=True, help_text="Organisation website."
#     )
#     email = models.EmailField(
#         max_length=254, blank=True, help_text="Organisation contact email."
#     )
#     external_reference = models.CharField(
#         max_length=100,
#         blank=True,
#         null=True,
#         db_index=True,
#         help_text="External system/import identifier. Unique only when the "
#         "integration requires it.",
#     )
#     metadata = models.JSONField(
#         default=dict,
#         blank=True,
#         help_text="Non-sensitive organisation-specific attributes only.",
#     )
#     is_active = models.BooleanField(
#         default=True,
#         help_text="Inactive records cannot be selected for new assignments.",
#     )

#     class Meta:
#         db_table = "tenancy_organization"
#         verbose_name = "Organization"
#         verbose_name_plural = "Organization"
#         ordering = ["tenant", "name"]
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["tenant", "code"],
#                 condition=Q(code__isnull=False),
#                 name="uniq_organization_tenant_code",
#             )           
#         ]

#     def clean(self):
#         super().clean()

#         if self.parent_id and self.parent_id == self.id:
#             raise ValidationError({
#                 "parent": "Organization cannot be its own parent."
#             })
            
#     def __str__(self):
#         return self.name

#     def save(self, *args, **kwargs):
#         if self.email:
#             self.email = self.email.lower()
#         super().save(*args, **kwargs)




# def tenant_logo_upload_path(instance, filename):
#     tenant_name = slugify(instance.name)
#     return os.path.join(tenant_name, f"{tenant_name}_docs", filename)


def tenant_document_upload_path(instance, filename):
    tenant_name = slugify(instance.tenant.name) if instance.tenant_id else "unassigned"
    return os.path.join(tenant_name, "tenant_documents", filename)


# # =====================================================================
# # 1. Core Tenant, TenantOperation, Organization — UNCHANGED from the
# #    real tenancy.py. Reproduced here only so this file is complete and
# #    importable on its own; do not diverge from the original.
# # =====================================================================

class Tenant(UUIDModel, TimeStampedModel):
    """Represents each customer tenant on the shared Qualion platform.

    Extends the original with sheet-16 fields not previously modeled
    (System Identity, Organisation Identity, Status & Audit sections).
    Everything else new from sheet 16/19 lives in its own table — see
    section 7 (TenantSettings) for why timezone/currency stay here.
    """

    class WorkspaceType(models.TextChoices):
        ORGANISATION = "ORGANISATION", "Organisation tenant"
        PERSONAL = "PERSONAL", "Personal workspace"

    class OrganisationType(models.TextChoices):
        CLIENT = "CLIENT", "Client"
        PMC = "PMC", "PMC"
        EPC = "EPC", "EPC Contractor"
        MANUFACTURER = "MANUFACTURER", "Manufacturer"
        INSPECTION_BODY = "INSPECTION_BODY", "Inspection Body"
        SHIPOWNER = "SHIPOWNER", "Shipowner"
        OPERATOR = "OPERATOR", "Operator"
        TRAINING_ORG = "TRAINING_ORG", "Training Organisation"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACTIVE = "ACTIVE", "Active"
        RESTRICTED = "RESTRICTED", "Restricted"
        SUSPENDED = "SUSPENDED", "Suspended"
        ARCHIVED = "ARCHIVED", "Archived"
        CLOSED = "CLOSED", "Closed"

    # --- System Identity ---
    name = models.CharField(
            max_length=200, null=True, blank=True,
            validators=[MinLengthValidator(2)],
            help_text="Tenant display name.",
        )
    code = models.CharField(
            max_length=50, null=True, blank=True,
            unique=True,
            validators=[validate_uppercase_code],
            help_text="Stable internal tenant code.",
        )
    workspace_type = models.CharField(
        max_length=20, choices=WorkspaceType.choices, null=True, blank=True,
        help_text="tenant.workspace_type — personal workspaces get no organisational privileges.",
    )

    # --- Organisation Identity ---
    legal_name = models.CharField(
            max_length=250,
             null=True, blank=True,
            help_text="Registered legal name, when different from display name.",
        )
    trade_name = models.CharField(max_length=200, null=True, blank=True)
    organisation_type = models.CharField(max_length=30, choices=OrganisationType.choices, null=True, blank=True)
    parent_tenant = models.ForeignKey(
        "self", on_delete=models.PROTECT, null=True, blank=True, related_name="child_tenants",
        help_text="tenant.parent_tenant_id — group hierarchy.",
    )
    description = models.TextField(blank=True, null=True, help_text="Max 2000 chars per blueprint.")
    website = models.URLField(max_length=500, null=True, blank=True)

    # --- Industry / Service Profile ---
    # tenant.industry_ids is modeled as TenantIndustry (many rows), see
    # section 3, so it can carry effective-date context.
    service_scope_ids = models.JSONField(default=list,  null=True, blank=True, help_text="tenant.service_scope_ids cache — see TenantScope for the authoritative rows.")

    # --- Platform access (pre-existing) ---    
    portal_slug = models.SlugField(
        max_length=80,
        unique=True, null=True, blank=True,
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
        max_length=64, null=True, blank=True,
        validators=[validate_iana_timezone],
        help_text="Default timezone used for tenant operations.",
    )
    default_currency = models.CharField(
        max_length=3, null=True, blank=True,
        validators=[validate_iso_currency_code],
        help_text="Default commercial currency.",
    )
    contact_email = models.EmailField(
        max_length=254, null=True, blank=True, help_text="Primary tenant contact email."
    )
    contact_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[validate_e164_phone],
        help_text="Primary tenant contact phone.",
    )
    settings = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="Feature flags and non-sensitive tenant configuration.",
    )
    branding = models.JSONField(
        default=dict,
        blank=True,
        null=True,
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
    
    # --- Status & Audit ---
    status_reason = models.TextField(blank=True, null=True, help_text="Required when status changes to RESTRICTED/SUSPENDED/ARCHIVED/CLOSED — enforce in serializer/service layer.")
    created_by = models.ForeignKey("accounts.UserTbl", on_delete=models.PROTECT, related_name="tenants_created")

    class Meta:
        db_table = "tenancy_tenant"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.parent_tenant_id and self.parent_tenant_id == self.pk:
            raise ValidationError({"parent_tenant": "Tenant cannot be its own parent."})

    def save(self, *args, **kwargs):
        if self.contact_email:
            self.contact_email = self.contact_email.lower()
        if self.portal_slug:
            self.portal_slug = self.portal_slug.lower()
        if self.custom_domain:
            self.custom_domain = self.custom_domain.lower()
        super().save(*args, **kwargs)


class TenantOperation(TimeStampedModel):
    """Unchanged from the real tenancy.py."""

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
        max_length=2, null=True, blank=True,
        validators=[validate_iso_country_code],
        help_text="Country of operation.",
    )
    region_name = models.CharField(
        max_length=120, null=True, blank=True, help_text="Optional state, province or region."
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
        constraints = [
            models.UniqueConstraint(fields=["tenant", "industry", "country_code"], name="uniq_tenant_operation"),
            models.CheckConstraint(
                check=Q(effective_from__isnull=True) | Q(effective_to__isnull=True) | Q(effective_from__lte=F("effective_to")),
                name="chk_tenant_operation_dates",
            ),
        ]


class Organization(UUIDModel, TimeStampedModel):
    """Unchanged from the real tenancy.py. External/business relationships
    (clients, employers, colleges). Referenced by resumes.ResumeTemplate
    .client_organization and experience.ProfessionalAssignment
    .organization — do not remove or rename fields on this model."""

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
        max_length=40, null=True, blank=True,
        choices=OrganizationType.choices,
        help_text="Business type of the organisation.",
    )
    name = models.CharField(
        max_length=200, null=True, blank=True,
        validators=[MinLengthValidator(2)],
        help_text="Display name.",
    )
    legal_name = models.CharField(max_length=250, null=True, blank=True, help_text="Legal name.")
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
         null=True, blank=True,
        validators=[validate_iso_country_code],
        help_text="Country location.",
    )
    city = models.CharField(max_length=120, null=True, blank=True, help_text="City location.")
    website = models.URLField(
        max_length=500, null=True, blank=True, help_text="Organisation website."
    )
    email = models.EmailField(
        max_length=254, null=True, blank=True, help_text="Organisation contact email."
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
        null=True, blank=True,
        help_text="Non-sensitive organisation-specific attributes only.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive records cannot be selected for new assignments.",
    )


    class Meta:
        db_table = "tenancy_organization"
        constraints = [models.UniqueConstraint(fields=["tenant", "code"], condition=Q(code__isnull=False), name="uniq_organization_tenant_code")]

    def clean(self):
        super().clean()
        if self.parent_id and self.parent_id == self.id:
            raise ValidationError({"parent": "Organization cannot be its own parent."})

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)



# =====================================================================
# 2. Legal Registration — all use TenantOwnedModel (PROTECT), not a
#    hand-rolled CASCADE tenant FK; Tenant/TenantOperation/Organization
#    above are the only documented CASCADE exceptions.
# =====================================================================

class TenantLegalEntity(UUIDModel, TenantOwnedModel, TimeStampedModel):
    registration_number = EncryptedCharField(max_length=100, help_text="Restricted PII/Legal per sheet 16 — encrypted at rest.")
    country_of_incorporation = models.CharField(max_length=2, validators=[validate_iso_country_code])
    incorporation_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "tenancy_tenant_legal_entity"


class TenantTaxRegistration(UUIDModel, TenantOwnedModel, TimeStampedModel):
    """Carries `tenant` directly via TenantOwnedModel, same as every other
    table here — even though it's also reachable via legal_entity.tenant.
    core/models.py states tenant_id belongs on every tenant-owned record;
    reaching it only through a join was the one table that broke that."""

    class TaxType(models.TextChoices):
        GST = "GST", "GST"
        VAT = "VAT", "VAT"
        TAX_ID = "TAX_ID", "Tax ID"

    legal_entity = models.ForeignKey(TenantLegalEntity, on_delete=models.CASCADE, related_name="tax_registrations")
    tax_type = models.CharField(max_length=20, choices=TaxType.choices)
    country_code = models.CharField(max_length=2, validators=[validate_iso_country_code])
    tax_number = EncryptedCharField(max_length=100, help_text="Encrypted at rest — same classification as TenantLegalEntity.registration_number.")
    status = models.CharField(max_length=20, default="ACTIVE")

    class Meta:
        db_table = "tenancy_tenant_tax_registration"


class TenantDomain(UUIDModel, TenantOwnedModel, TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        VERIFIED = "VERIFIED", "Verified"
        FAILED = "FAILED", "Failed"

    domain = models.CharField(max_length=255)
    verification_status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tenancy_tenant_domain"
        constraints = [models.UniqueConstraint(fields=["tenant", "domain"], name="uniq_tenant_domain")]


# =====================================================================
# 3. Industry / Scope declaration — reuses catalog.ReferenceValue and
#    catalog.ScopeCatalog exactly as confirmed in catalog.py. No local
#    stub tables.
# =====================================================================

class TenantIndustry(UUIDModel, TenantOwnedModel, TimeStampedModel):
    """tenant.industry_ids. industry.option_set.option_type must be
    'INDUSTRY' — enforce in clean()/serializer, catalog has no CHECK for it."""

    industry = models.ForeignKey("catalog.ReferenceValue", on_delete=models.PROTECT, related_name="tenant_industries")

    class Meta:
        db_table = "tenancy_tenant_industry"
        constraints = [models.UniqueConstraint(fields=["tenant", "industry"], name="uniq_tenant_industry")]


class TenantScope(UUIDModel, TenantOwnedModel, TimeStampedModel):
    """tenant.service_scope_ids as relational rows — the authoritative
    source; Tenant.service_scope_ids is a non-authoritative cache, same
    pattern as professional_profiles.scope_experience_codes elsewhere."""

    scope_catalog = models.ForeignKey("catalog.ScopeCatalog", on_delete=models.PROTECT, related_name="tenant_scopes")

    class Meta:
        db_table = "tenancy_tenant_scope"
        constraints = [models.UniqueConstraint(fields=["tenant", "scope_catalog"], name="uniq_tenant_scope")]


# =====================================================================
# 4. Business Units & Locations
# =====================================================================

class TenantBusinessUnit(UUIDModel, TenantOwnedModel, TimeStampedModel):
    """tenant_business_units — internal division structure. Distinct from
    Organization (external relationships) and TenantLocation (addresses)."""

    legal_entity = models.ForeignKey(TenantLegalEntity, on_delete=models.SET_NULL, null=True, blank=True, related_name="business_units")
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey("accounts.UserTbl", on_delete=models.PROTECT, related_name="owned_business_units")
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, default="ACTIVE")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "tenancy_tenant_business_unit"
        constraints = [models.UniqueConstraint(fields=["tenant", "code"], name="uniq_business_unit_code")]

    def __str__(self):
        return self.name


class TenantLocation(UUIDModel, TenantOwnedModel, TimeStampedModel):
    class LocationType(models.TextChoices):
        REGISTERED = "REGISTERED", "Registered office"
        CORPORATE = "CORPORATE", "Corporate office"
        BILLING = "BILLING", "Billing address"
        BRANCH = "BRANCH", "Branch"
        PROJECT_OFFICE = "PROJECT_OFFICE", "Project office"
        FACTORY = "FACTORY", "Factory"
        YARD = "YARD", "Yard"
        PORT_SITE = "PORT_SITE", "Port site"

    business_unit = models.ForeignKey(TenantBusinessUnit, on_delete=models.SET_NULL, null=True, blank=True, related_name="locations")
    location_type = models.CharField(max_length=20, choices=LocationType.choices)
    location_code = models.CharField(max_length=100, blank=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country_code = models.CharField(max_length=2, validators=[validate_iso_country_code])
    timezone = models.CharField(max_length=64, validators=[validate_iana_timezone])
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_head_office = models.BooleanField(default=False)
    is_default_billing = models.BooleanField(default=False)
    is_default_project_location = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "tenancy_tenant_location"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "location_code"],
                condition=Q(location_code__isnull=False) & ~Q(location_code=""),
                name="uniq_location_code_per_tenant",
            ),
        ]

    def __str__(self):
        return f"{self.tenant} — {self.get_location_type_display()}"


# =====================================================================
# 5. Authorised Representatives & Contacts
# =====================================================================

class TenantAuthorisedRepresentative(UUIDModel, TenantOwnedModel, TimeStampedModel):
    class AuthorityType(models.TextChoices):
        DIRECTOR = "DIRECTOR", "Director"
        POWER_OF_ATTORNEY = "POWER_OF_ATTORNEY", "Power of Attorney"
        DESIGNATED_SIGNATORY = "DESIGNATED_SIGNATORY", "Designated Signatory"

    user = models.ForeignKey("accounts.UserTbl", on_delete=models.SET_NULL, null=True, blank=True, related_name="representative_of")
    full_name = models.CharField(max_length=255)
    title = models.CharField(max_length=100, blank=True)
    official_email = models.EmailField()
    mobile = models.CharField(max_length=20, validators=[validate_e164_phone])
    authority_type = models.CharField(max_length=30, choices=AuthorityType.choices)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    # Reuses the platform's shared verification vocabulary (SELF_DECLARED /
    # UNDER_REVIEW / VERIFIED / ... from core.choices) instead of a new enum.
    verification_status = models.CharField(max_length=30, choices=VerificationStatus.choices, default=VerificationStatus.SELF_DECLARED)
    evidence_document = models.ForeignKey("TenantDocument", on_delete=models.SET_NULL, null=True, blank=True, related_name="representative_proofs")

    class Meta:
        db_table = "tenancy_tenant_authorised_representative"


class TenantContact(UUIDModel, TenantOwnedModel, TimeStampedModel):
    class ContactType(models.TextChoices):
        ORG_ADMIN = "ORG_ADMIN", "Organisation Admin"
        TECHNICAL = "TECHNICAL", "Technical"
        PROJECT = "PROJECT", "Project"
        FINANCE = "FINANCE", "Finance"
        LEGAL = "LEGAL", "Legal"
        SECURITY = "SECURITY", "Security"

    contact_type = models.CharField(max_length=20, choices=ContactType.choices)
    user = models.ForeignKey("accounts.UserTbl", on_delete=models.SET_NULL, null=True, blank=True, related_name="tenant_contact_roles")
    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "tenancy_tenant_contact"


# =====================================================================
# 6. Verification & Documents
# =====================================================================

class TenantVerification(UUIDModel, TenantOwnedModel, CreatedOnlyModel):
    """Append-only history — insert a new row on every status change,
    never update in place (same pattern as CompetencyAssessment)."""

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
        RETURNED = "RETURNED", "Returned"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        SUSPENDED = "SUSPENDED", "Suspended"
        EXPIRED = "EXPIRED", "Expired"

    class RiskClassification(models.TextChoices):
        LOW = "LOW", "Low"
        STANDARD = "STANDARD", "Standard"
        ENHANCED_REVIEW = "ENHANCED_REVIEW", "Enhanced Review"
        RESTRICTED = "RESTRICTED", "Restricted"

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey("accounts.UserTbl", on_delete=models.SET_NULL, null=True, blank=True, related_name="tenant_reviews_done")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(blank=True)
    risk_classification = models.CharField(max_length=20, choices=RiskClassification.choices, default=RiskClassification.STANDARD)
    next_review_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "tenancy_tenant_verification"
        ordering = ["-created_at"]


class TenantDocument(UUIDModel, TenantOwnedModel, TimeStampedModel, ArchivableModel):
    class DocumentType(models.TextChoices):
        REGISTRATION = "REGISTRATION", "Registration"
        TAX = "TAX", "Tax"
        ADDRESS = "ADDRESS", "Address Proof"
        AUTHORISATION = "AUTHORISATION", "Authorisation"
        LICENCE = "LICENCE", "Licence"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        EXPIRED = "EXPIRED", "Expired"
        SUPERSEDED = "SUPERSEDED", "Superseded"
        REJECTED = "REJECTED", "Rejected"

    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    file = models.FileField(upload_to=tenant_document_upload_path, max_length=1000, validators=[MaxFileSizeValidator(MAX_TENANT_LOGO_SIZE_BYTES)])
    file_hash = models.CharField(max_length=128)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    reviewed_by = models.ForeignKey("accounts.UserTbl", on_delete=models.SET_NULL, null=True, blank=True, related_name="tenant_documents_reviewed")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    superseded_by = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="supersedes")

    class Meta:
        db_table = "tenancy_tenant_document"


# =====================================================================
# 7. Legal, Confidentiality & Settings
# =====================================================================


class TenantLegalAcceptance(UUIDModel, TenantOwnedModel, CreatedOnlyModel):
    class AcceptanceType(models.TextChoices):
        TERMS = "TERMS", "Platform Terms"
        DPA = "DPA", "Data Processing Terms"

    acceptance_type = models.CharField(max_length=10, choices=AcceptanceType.choices)
    version = models.CharField(max_length=50)
    accepted_by = models.ForeignKey("accounts.UserTbl", on_delete=models.PROTECT, related_name="tenant_acceptances")
    jurisdiction = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "tenancy_tenant_legal_acceptance"


class TenantLegalSettings(UUIDModel, TenantOwnedModel):
    """1:1 with tenant via unique=True below — deliberately its own table
    for Restricted/Legal access control."""

    class NdaRequirement(models.TextChoices):
        NOT_REQUIRED = "NOT_REQUIRED", "Not Required"
        TENANT_STANDARD = "TENANT_STANDARD", "Tenant Standard NDA"
        PROJECT_SPECIFIC = "PROJECT_SPECIFIC", "Project-Specific"
        MUTUAL_NDA = "MUTUAL_NDA", "Mutual NDA"

    class Classification(models.TextChoices):
        PUBLIC = "PUBLIC", "Public"
        INTERNAL = "INTERNAL", "Internal"
        CONFIDENTIAL = "CONFIDENTIAL", "Confidential"
        RESTRICTED = "RESTRICTED", "Restricted"

    tenant = models.OneToOneField(Tenant, on_delete=models.PROTECT, related_name="legal_settings")
    nda_requirement = models.CharField(max_length=20, choices=NdaRequirement.choices, default=NdaRequirement.NOT_REQUIRED)
    default_classification = models.CharField(max_length=20, choices=Classification.choices, default=Classification.INTERNAL)
    retention_policy = models.CharField(max_length=100, blank=True)
    is_legal_hold = models.BooleanField(default=False, help_text="Blocks retention/deletion jobs while true — RETENTION_APPLY must check this first.")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenancy_tenant_legal_settings"


class TenantNda(UUIDModel, TenantOwnedModel, CreatedOnlyModel):
    version = models.CharField(max_length=50)
    parties = models.JSONField(default=list)
    signatories = models.JSONField(default=list)
    effective_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    evidence_document = models.ForeignKey(TenantDocument, on_delete=models.SET_NULL, null=True, blank=True, related_name="ndas")

    class Meta:
        db_table = "tenancy_tenant_nda"


class TenantSettings(UUIDModel, TenantOwnedModel):
    """1:1 with tenant. Timezone/currency stay on Tenant itself (sheet
    16's Database Path points them there); this covers the remaining
    localisation fields sheet 19 lists separately."""

    tenant = models.OneToOneField(Tenant, on_delete=models.PROTECT, related_name="tenant_settings")
    default_language = models.CharField(max_length=10, default="en")
    date_format = models.CharField(max_length=20, default="DD-MM-YYYY")
    number_format = models.CharField(max_length=20, default="1,234.56")
    measurement_system = models.CharField(max_length=10, choices=[("METRIC", "Metric"), ("IMPERIAL", "Imperial"), ("MIXED", "Mixed")], default="METRIC")
    working_calendar = models.CharField(max_length=100, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenancy_tenant_settings"


# =====================================================================
# 8. Subscription & Modules
# =====================================================================

    
class TenantSubscription(UUIDModel, TenantOwnedModel, TimeStampedModel):
    """Versioned — insert a new row per plan change, never edit in place."""

    class Plan(models.TextChoices):
        PILOT = "PILOT", "Pilot"
        STANDARD = "STANDARD", "Standard"
        ENTERPRISE = "ENTERPRISE", "Enterprise"

    class Status(models.TextChoices):
        TRIAL = "TRIAL", "Trial"
        ACTIVE = "ACTIVE", "Active"
        PAST_DUE = "PAST_DUE", "Past Due"
        SUSPENDED = "SUSPENDED", "Suspended"
        CANCELLED = "CANCELLED", "Cancelled"
        EXPIRED = "EXPIRED", "Expired"

    plan = models.CharField(max_length=20, choices=Plan.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TRIAL)
    start_date = models.DateField()
    renewal_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    seat_limit = models.PositiveIntegerField()
    project_limit = models.PositiveIntegerField(null=True, blank=True)
    storage_limit_gb = models.PositiveIntegerField(null=True, blank=True)
    used_seats = models.PositiveIntegerField(default=0)
    used_projects = models.PositiveIntegerField(default=0)
    used_storage_gb = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = "tenancy_tenant_subscription"
        ordering = ["-created_at"]


class Module(UUIDModel, TimeStampedModel):
    """Platform-level feature modules (SMS, LPMS, TPI, AUDIT,
    RESUME_BUILDER) — no tenant FK, shared master like ReferenceValue.

    NOTE: catalog/models.py's own docstring states tenant-agnostic master
    tables belong in catalog, not their consuming app. This table arguably
    belongs there rather than here — kept in tenancy for now since only
    tenancy consumes it, but flagging rather than silently deciding."""

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "tenancy_module"

    def __str__(self):
        return self.code


class TenantModuleEntitlement(UUIDModel, TenantOwnedModel, TimeStampedModel):
    module = models.ForeignKey(Module, on_delete=models.PROTECT, related_name="tenant_entitlements")
    status = models.CharField(max_length=20, default="ACTIVE")
    limits = models.JSONField(default=dict, blank=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "tenancy_tenant_module_entitlement"
        constraints = [models.UniqueConstraint(fields=["tenant", "module"], name="uniq_tenant_module")]


# =====================================================================
# 9. Branding & Templates
# =====================================================================


class TenantBranding(UUIDModel, TenantOwnedModel):
    tenant = models.OneToOneField(Tenant, on_delete=models.PROTECT, related_name="tenant_branding")
    logo = models.ImageField(upload_to="tenant_branding/logos/", max_length=1000, null=True, blank=True, validators=[MaxFileSizeValidator(MAX_TENANT_LOGO_SIZE_BYTES)])
    colours = models.JSONField(default=dict, blank=True)
    report_header = models.TextField(blank=True)
    report_footer = models.TextField(blank=True)
    disclaimer_text = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenancy_tenant_branding"

#no apis
class TenantResumeTemplate(TenantOwnedModel, TimeStampedModel):
    """NOTE: resumes.ResumeTemplate already exists, keyed to
    tenant + tenancy.Organization (client_organization), with full
    mapping_schema/confidentiality_rules/publication workflow — it is NOT
    a stub, it's a complete, more capable table than this one. This
    tenant-level table should probably not exist at all; use
    resumes.ResumeTemplate directly instead. Kept here only as a
    placeholder in case "tenant's own default template list" turns out
    to be a genuinely separate concept from "per-client template" —
    confirm with the team before building on this table."""

    template_name = models.CharField(max_length=255)
    file = models.FileField(upload_to="tenant_templates/resume/", max_length=1000)
    version = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default="DRAFT")

    class Meta:
        db_table = "tenancy_tenant_resume_template"


class TenantReportTemplate(UUIDModel, TenantOwnedModel, TimeStampedModel):
    template_name = models.CharField(max_length=255)
    file = models.FileField(upload_to="tenant_templates/report/", max_length=1000)
    version = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default="DRAFT")
    approval_matrix = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "tenancy_tenant_report_template"


# =====================================================================
# 10. Security
# =====================================================================


class TenantSecuritySettings(UUIDModel, TenantOwnedModel):
    class MfaPolicy(models.TextChoices):
        OPTIONAL = "OPTIONAL", "Optional"
        REQUIRED_FOR_ADMINS = "REQUIRED_FOR_ADMINS", "Required for Admins"
        REQUIRED_FOR_ALL = "REQUIRED_FOR_ALL", "Required for All"

    class SsoStatus(models.TextChoices):
        DISABLED = "DISABLED", "Disabled"
        CONFIGURING = "CONFIGURING", "Configuring"
        ACTIVE = "ACTIVE", "Active"
        SUSPENDED = "SUSPENDED", "Suspended"

    class ApiAccessStatus(models.TextChoices):
        DISABLED = "DISABLED", "Disabled"
        SANDBOX = "SANDBOX", "Sandbox"
        PRODUCTION = "PRODUCTION", "Production"

    tenant = models.OneToOneField(Tenant, on_delete=models.PROTECT, related_name="security_settings")
    mfa_policy = models.CharField(max_length=25, choices=MfaPolicy.choices, default=MfaPolicy.OPTIONAL)
    sso_status = models.CharField(max_length=15, choices=SsoStatus.choices, default=SsoStatus.DISABLED)
    identity_provider = models.CharField(max_length=100, blank=True)
    session_policy = models.JSONField(default=dict, blank=True)
    api_access_status = models.CharField(max_length=15, choices=ApiAccessStatus.choices, default=ApiAccessStatus.DISABLED)
    export_policy = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenancy_tenant_security_settings"


class TenantIPRestriction(UUIDModel):
    security_settings = models.ForeignKey(TenantSecuritySettings, on_delete=models.CASCADE, related_name="ip_restrictions")
    cidr_range = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tenancy_tenant_ip_restriction"


class TenantIntegration(UUIDModel, TenantOwnedModel, TimeStampedModel):
    integration_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default="ACTIVE")
    secret_reference = EncryptedCharField(max_length=255, help_text="Never exported; encrypted at rest.")
    scopes = models.JSONField(default=list, blank=True)
    rotated_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tenancy_tenant_integration"


# =====================================================================
# 11. Billing
# =====================================================================

class TenantBilling(UUIDModel, TenantOwnedModel):
    tenant = models.OneToOneField(Tenant, on_delete=models.PROTECT, related_name="billing")
    billing_entity = models.ForeignKey(TenantLegalEntity, on_delete=models.SET_NULL, null=True, blank=True, related_name="billing_for")
    po_required = models.BooleanField(default=False)
    po_format = models.CharField(max_length=100, blank=True)
    po_contact = models.CharField(max_length=255, blank=True)
    payment_terms = models.CharField(max_length=100, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenancy_tenant_billing"


# =====================================================================
# 12. Membership & RBAC — role FK points at accounts.roles (the real
#     table with rows), never accounts.RoleCode (a TextChoices, not a
#     model — cannot be a ForeignKey target).
# =====================================================================

#no api
class TenantMembership(TenantOwnedModel, TimeStampedModel):
    """OPEN DESIGN QUESTION, not resolved by this file: accounts.UserTbl
    .tenant is a single, non-null-except-Super-Admin FK — the current
    registration flow implies one UserTbl row per tenant per person. This
    model assumes the opposite: one shared identity with many-to-many
    membership across tenants via multiple TenantMembership rows. Those
    two models are incompatible as written. Confirm with whoever owns
    accounts before building anything on top of TenantMembership — do
    not assume this is settled just because it compiles."""

    class Status(models.TextChoices):
        INVITED = "INVITED", "Invited"
        ACTIVE = "ACTIVE", "Active"
        REMOVED = "REMOVED", "Removed"
        EXPIRED = "EXPIRED", "Expired"

    user = models.ForeignKey("accounts.UserTbl", on_delete=models.CASCADE, related_name="tenant_memberships")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.INVITED)
    invited_by = models.ForeignKey("accounts.UserTbl", on_delete=models.SET_NULL, null=True, blank=True, related_name="tenant_memberships_invited")
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)
    last_active_at = models.DateTimeField(null=True, blank=True, help_text="Drives DORMANT_REVIEW — update on each authenticated request/session.")

    class Meta:
        db_table = "tenancy_tenant_membership"
        constraints = [models.UniqueConstraint(fields=["tenant", "user"], name="uniq_tenant_membership")]

#no api
class TenantRoleAssignment(UUIDModel):
    membership = models.ForeignKey(TenantMembership, on_delete=models.CASCADE, related_name="role_assignments")
    role = models.ForeignKey("accounts.roles", on_delete=models.PROTECT, related_name="tenant_assignments")
    granted_by = models.ForeignKey("accounts.UserTbl", on_delete=models.PROTECT, related_name="tenant_roles_granted")
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default="ACTIVE")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tenancy_tenant_role_assignment"


class TenantInvitation(UUIDModel, TenantOwnedModel):
    email = models.EmailField()
    role = models.ForeignKey("accounts.roles", on_delete=models.PROTECT, related_name="tenant_invitations")
    token = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, default="SENT")
    sent_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "tenancy_tenant_invitation"


# =====================================================================
# 13. Workflow & Operational Logging
# =====================================================================

class TenantWorkflow(UUIDModel, TenantOwnedModel, TimeStampedModel):
    workflow_type = models.CharField(max_length=50)
    reference_table = models.CharField(max_length=50)
    reference_id = models.UUIDField()
    status = models.CharField(max_length=20, default="IN_PROGRESS")

    class Meta:
        db_table = "tenancy_tenant_workflow"


class TenantWorkflowStep(UUIDModel):
    workflow = models.ForeignKey(TenantWorkflow, on_delete=models.CASCADE, related_name="steps")
    step_order = models.PositiveIntegerField()
    assigned_role = models.ForeignKey("accounts.roles", on_delete=models.PROTECT, related_name="workflow_steps")
    decision = models.CharField(max_length=30, blank=True)
    comments = models.TextField(blank=True)
    actioned_by = models.ForeignKey("accounts.UserTbl", on_delete=models.SET_NULL, null=True, blank=True, related_name="workflow_steps_actioned")
    actioned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tenancy_tenant_workflow_step"
        ordering = ["workflow", "step_order"]


class TenantOperationLog(UUIDModel, TenantOwnedModel):
    """Lightweight operational log for long-running tenant-side actions.
    NOT a substitute for governance.AuditEvent (the real, existing
    polymorphic audit table via content_type/object_id) — that already
    covers per-record before/after audit trails. This is only for
    tracking async job runs (bulk import, retention sweep, etc)."""

    operation_type = models.CharField(max_length=100)
    performed_by = models.ForeignKey("accounts.UserTbl", on_delete=models.SET_NULL, null=True, blank=True, related_name="tenant_operations_performed")
    status = models.CharField(max_length=20, default="STARTED")
    remarks = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tenancy_tenant_operation_log"


# =====================================================================
# 14. Configuration extras (sheet 17 operation-code gaps)
# =====================================================================


class TenantTerminology(UUIDModel, TenantOwnedModel):
    canonical_code = models.CharField(max_length=100, help_text="System term, e.g. 'PROJECT'.")
    display_label = models.CharField(max_length=100, help_text="Tenant's local term, e.g. 'Assignment'.")

    class Meta:
        db_table = "tenancy_tenant_terminology"
        constraints = [models.UniqueConstraint(fields=["tenant", "canonical_code"], name="uniq_tenant_terminology")]


class TenantNumberingConfig(UUIDModel, TenantOwnedModel):
    document_type = models.CharField(max_length=30)
    pattern = models.CharField(max_length=100, help_text="e.g. 'PRJ-{YYYY}-{SEQ}'.")
    current_sequence = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "tenancy_tenant_numbering_config"
        constraints = [models.UniqueConstraint(fields=["tenant", "document_type"], name="uniq_tenant_numbering")]


class TenantApprovalMatrix(UUIDModel, TenantOwnedModel, TimeStampedModel):
    """Tenant-wide default; a Project may override via its own row."""

    project = models.ForeignKey("Project", on_delete=models.CASCADE, null=True, blank=True, related_name="approval_matrix_overrides")
    document_type = models.CharField(max_length=20, choices=[("PROJECT", "Project"), ("REPORT", "Report")])
    sequence = models.JSONField(default=list, help_text="Ordered list of accounts.roles codes required to approve.")

    class Meta:
        db_table = "tenancy_tenant_approval_matrix"


class TenantNotificationSettings(UUIDModel, TenantOwnedModel, TimeStampedModel):
    event_type = models.CharField(max_length=100)
    channels = models.JSONField(default=list, blank=True)
    escalation_rules = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "tenancy_tenant_notification_settings"


class ConflictOfInterestDeclaration(UUIDModel, TenantOwnedModel, TimeStampedModel):
    project = models.ForeignKey("Project", on_delete=models.SET_NULL, null=True, blank=True, related_name="coi_declarations")
    declared_by = models.ForeignKey("accounts.UserTbl", on_delete=models.PROTECT, related_name="coi_declarations")
    has_conflict = models.BooleanField()
    details = models.TextField(blank=True)
    mitigation = models.TextField(blank=True)
    status = models.CharField(max_length=20, default="SUBMITTED")
    reviewed_by = models.ForeignKey("accounts.UserTbl", on_delete=models.SET_NULL, null=True, blank=True, related_name="coi_reviews_done")
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tenancy_conflict_of_interest_declaration"


class DataExportRequest(UUIDModel, TenantOwnedModel, TimeStampedModel):
    requested_by = models.ForeignKey("accounts.UserTbl", on_delete=models.PROTECT, related_name="export_requests_made")
    purpose = models.TextField()
    scope = models.JSONField(default=dict)
    status = models.CharField(max_length=20, default="REQUESTED")
    approved_by = models.ForeignKey("accounts.UserTbl", on_delete=models.SET_NULL, null=True, blank=True, related_name="export_requests_approved")
    approved_at = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    watermark_applied = models.BooleanField(default=False)

    class Meta:
        db_table = "tenancy_data_export_request"


# =====================================================================
# 15. Projects — the tenant's own work requisition (job opening, before
#     any candidate is attached). NOT the same as experience.ProjectRecord
#     (a candidate's own resume entry of past work already performed) —
#     see module docstring. Once a candidate is placed, link out to
#     experience.ProfessionalAssignment / experience.ProjectScope rather
#     than re-storing the same authority/allocation data twice.
# =====================================================================

class Project(TenantOwnedModel, TimeStampedModel, UUIDModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        OPEN = "OPEN", "Open"
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    class Confidentiality(models.TextChoices):
        PUBLIC = "PUBLIC", "Public"
        INTERNAL = "INTERNAL", "Internal"
        CONFIDENTIAL = "CONFIDENTIAL", "Confidential"
        RESTRICTED = "RESTRICTED", "Restricted"

    business_unit = models.ForeignKey(TenantBusinessUnit, on_delete=models.SET_NULL, null=True, blank=True, related_name="projects")
    location = models.ForeignKey(TenantLocation, on_delete=models.SET_NULL, null=True, blank=True, related_name="projects")
    project_code = models.CharField(max_length=50)
    project_name = models.CharField(max_length=250)
    project_type = models.CharField(max_length=100, blank=True)
    # Fixed: was `CharField` with FK kwargs (invalid Django, raises TypeError
    # at import time). FKs the same Organization table
    # resumes.ResumeTemplate.client_organization already uses.
    client_organization = models.ForeignKey(Organization, on_delete=models.PROTECT, null=True, blank=True, related_name="client_projects")
    industry = models.ForeignKey("catalog.ReferenceValue", on_delete=models.PROTECT, null=True, blank=True, related_name="projects")
    scope_catalog_entries = models.ManyToManyField("catalog.ScopeCatalog", blank=True, related_name="projects")
    country_code = models.CharField(max_length=2, validators=[validate_iso_country_code])
    city = models.CharField(max_length=120, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    confidentiality_classification = models.CharField(max_length=20, choices=Confidentiality.choices, default=Confidentiality.INTERNAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "tenancy_project"
        constraints = [models.UniqueConstraint(fields=["tenant", "project_code"], name="uniq_project_code_per_tenant")]

    def __str__(self):
        return self.project_name

#no api
class ProjectMembership(models.Model):
    """Internal tenant staff assigned to manage a project — distinct from
    ProjectPlacement below, which is the external candidate's placement."""

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="memberships")
    membership = models.ForeignKey(TenantMembership, on_delete=models.CASCADE, related_name="project_memberships")
    role = models.ForeignKey("accounts.roles", on_delete=models.PROTECT, related_name="project_memberships")
    scopes = models.JSONField(default=list, blank=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    entitlement = models.JSONField(default=dict, blank=True)
    assigned_by = models.ForeignKey("accounts.UserTbl", on_delete=models.PROTECT, related_name="project_memberships_assigned")

    class Meta:
        db_table = "tenancy_project_membership"
        constraints = [models.UniqueConstraint(fields=["project", "membership"], name="uniq_project_membership")]


class ProjectRequirement(UUIDModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="requirements")
    # Fixed: was `CharField` with FK kwargs. FKs the Role_Master lookup —
    # same table professionals.ProfessionalProfile.primary_role uses
    # (option_set.option_type=PROFESSIONAL_ROLE), not primary_role_code
    # as I'd mis-stated in an earlier version of this comment.
    role_code = models.ForeignKey("catalog.ReferenceValue", on_delete=models.PROTECT, related_name="project_requirements")
    required_count = models.PositiveIntegerField()
    minimum_experience_years = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_mandatory = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = "tenancy_project_requirement"


class ProjectRequirementScope(UUIDModel):
    requirement = models.ForeignKey(ProjectRequirement, on_delete=models.CASCADE, related_name="scopes")
    scope_catalog = models.ForeignKey("catalog.ScopeCatalog", on_delete=models.PROTECT, related_name="requirement_links")

    class Meta:
        db_table = "tenancy_project_requirement_scope"
        constraints = [models.UniqueConstraint(fields=["requirement", "scope_catalog"], name="uniq_requirement_scope")]


class ProjectCandidate(UUIDModel):
    """Shortlist stage — masked, pre-disclosure."""

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="candidates")
    professional = models.ForeignKey("professionals.ProfessionalProfile", on_delete=models.PROTECT, related_name="project_shortlists")
    shortlist_status = models.CharField(max_length=30, default="SHORTLISTED")
    shortlisted_by = models.ForeignKey("accounts.UserTbl", on_delete=models.PROTECT, related_name="shortlists_made")

    class Meta:
        db_table = "tenancy_project_candidate"
        constraints = [models.UniqueConstraint(fields=["project", "professional"], name="uniq_project_candidate")]


class DisclosureRequest(TenantOwnedModel, TimeStampedModel, UUIDModel):
    """Fixed: was defined twice in the source draft (second definition
    silently overwrote the first). Added requested_fields/purpose — sheet
    19 requires disclosure to be field-level and purpose-bound. PROTECT
    (not CASCADE) on project/professional — deleting a project must not
    erase the record of what a candidate consented to."""

    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        APPROVED = "APPROVED", "Approved"
        DECLINED = "DECLINED", "Declined"
        EXPIRED = "EXPIRED", "Expired"

    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name="disclosure_requests")
    professional = models.ForeignKey("professionals.ProfessionalProfile", on_delete=models.PROTECT, related_name="disclosure_requests")
    requested_by = models.ForeignKey("accounts.UserTbl", on_delete=models.PROTECT, related_name="disclosure_requests_made")
    requested_fields = models.JSONField(default=list, help_text="Which profile fields are being requested.")
    purpose = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tenancy_disclosure_request"


class CandidateConsent(UUIDModel):
    """Was entirely missing from the previous draft. Central to the
    platform principle that the tenant never owns the candidate's full
    profile — only what's explicitly consented, field by field. PROTECT
    on both FKs, same reasoning as DisclosureRequest above."""

    class Decision(models.TextChoices):
        GRANTED = "GRANTED", "Granted"
        DECLINED = "DECLINED", "Declined"
        WITHDRAWN = "WITHDRAWN", "Withdrawn"

    disclosure_request = models.ForeignKey(DisclosureRequest, on_delete=models.PROTECT, related_name="consents")
    professional = models.ForeignKey("professionals.ProfessionalProfile", on_delete=models.PROTECT, related_name="consents_given")
    decision = models.CharField(max_length=15, choices=Decision.choices)
    fields = models.JSONField(default=list, help_text="Subset of requested_fields actually consented to.")
    decided_at = models.DateTimeField(auto_now_add=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tenancy_candidate_consent"


class ProjectPlacement(UUIDModel):
    """Renamed from the previous draft's `ProjectAssignment` to avoid
    confusion with the real experience.ProfessionalAssignment. This is
    the tenant-side placement record (requisition fulfilled); once
    confirmed, link it to the candidate's own resume-facing
    experience.ProfessionalAssignment row via the field below so the
    same placement isn't described twice with two different shapes."""

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="placements")
    professional = models.ForeignKey("professionals.ProfessionalProfile", on_delete=models.PROTECT, related_name="project_placements")
    professional_assignment = models.ForeignKey(
        "experience.ProfessionalAssignment", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="tenant_placement",
        help_text="Link to the candidate's own experience.ProfessionalAssignment "
        "row (assignment_type=PROJECT) once the placement is confirmed.",
    )
    assigned_role = models.CharField(max_length=120)
    deployment_start = models.DateField()
    deployment_end = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default="ACTIVE")

    class Meta:
        db_table = "tenancy_project_placement"


class ProjectScopeLink(UUIDModel, TimeStampedModel):
    """Per-scope technical-experience claim on the tenant side: authority
    exercised, allocation %, verified field days. Mirrors
    experience.ProjectScope in shape but is tenant-owned (tied to this
    requisition's Project, not the candidate's own ProjectRecord).
    Link to experience.ProjectScope once the candidate's resume entry
    for this placement is created, rather than treating the two as
    independent sources of truth for the same claim."""

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="scope_links")
    placement = models.ForeignKey(ProjectPlacement, on_delete=models.SET_NULL, null=True, blank=True, related_name="scope_links")
    professional = models.ForeignKey("professionals.ProfessionalProfile", on_delete=models.PROTECT, related_name="project_scope_links")
    experience_project_scope = models.ForeignKey(
        "experience.ProjectScope", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="tenant_scope_link",
        help_text="Link to the matching candidate-side experience.ProjectScope row, once created.",
    )
    industry = models.ForeignKey("catalog.ReferenceValue", on_delete=models.PROTECT, related_name="project_scope_links")
    scope_catalog = models.ForeignKey("catalog.ScopeCatalog", on_delete=models.PROTECT, related_name="project_scope_links")
    authority_action_code = models.ForeignKey(
        "catalog.ReferenceValue", on_delete=models.PROTECT, related_name="project_scope_link_authority",
        help_text="option_set.option_type must be AUTHORITY_ACTION, matching experience.ProjectScope.authority_action.",
    )
    allocation_percent = models.PositiveSmallIntegerField()
    verified_field_days = models.PositiveIntegerField(null=True, blank=True)
    evidence_document = models.ForeignKey(TenantDocument, on_delete=models.SET_NULL, null=True, blank=True, related_name="scope_link_evidence")

    class Meta:
        db_table = "tenancy_project_scope_link"
        constraints = [models.UniqueConstraint(fields=["project", "professional", "scope_catalog"], name="uniq_project_scope_link")]







