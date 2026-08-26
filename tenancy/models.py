"""tenancy: platform tenants, their legal/organisational structure,
membership, security, subscription, branding, and tenant-owned work
requisitions (projects, requirements, shortlisting, disclosure, consent).

Ownership and access: Platform Super Admin creates and closes tenants.
Organisation Admin manages day-to-day records within their own tenant.

=====================================================================
Design notes
=====================================================================

  - Every field carries an inline comment explaining its purpose, and a
    sheet-16 field-ID reference where one exists.
  - accounts.roles is the real role table with actual rows.
    accounts.RoleCode is a TextChoices enum, not a table, and cannot be
    an FK target.
  - core.TenantOwnedModel (default on_delete=PROTECT) is used for every
    tenant-owned table below. CASCADE is used only for
    Tenant / TenantOperation / Organization, matching the documented
    exception in core/models.py.
  - Real user model: accounts.UserTbl. Real scope table:
    catalog.ScopeCatalog. Real professional table:
    professionals.ProfessionalProfile.
  - experience.ProjectRecord / ProjectScope / ProfessionalAssignment are
    the candidate's own resume-facing records — linked to, not
    duplicated by, this file's Project / ProjectPlacement / ProjectScopeLink.
  - Sensitive strings (registration numbers, tax numbers, integration
    secrets) use core.fields.EncryptedCharField.
  - accounts.UserTbl is tenant-scoped by design, confirmed against its
    own docstring: one row per tenant per person, login identity is
    tenant + email, UserTbl.tenant is a direct required FK (NULL only
    for Platform Super Admin). There is no separate tenant-membership
    bridge table — UserTbl.tenant already is that relationship.
    TenantRoleAssignment FKs UserTbl directly, not through any
    intermediate membership table.
  - Resume templates use resumes.ResumeTemplate directly — its
    client_organization FK is nullable, which already covers "the
    tenant's own default template, not tied to a specific client."
    There is no separate tenant-level resume template table.
=====================================================================
"""

import os

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
    validate_iana_timezone,
    validate_iso_country_code,
    validate_iso_currency_code,
    validate_lowercase_slug,
    validate_uppercase_code,
)

MAX_TENANT_LOGO_SIZE_BYTES = 10 * 1024 * 1024


def tenant_logo_upload_path(instance, filename):
    # Builds the storage path for a tenant's logo file: <tenant>/<tenant>_docs/<filename>
    tenant_name = slugify(instance.name)
    return os.path.join(tenant_name, f"{tenant_name}_docs", filename)


def tenant_document_upload_path(instance, filename):
    # Same idea, for any tenant compliance document (registration proof, tax cert, etc.)
    tenant_name = slugify(instance.tenant.name) if instance.tenant_id else "unassigned"
    return os.path.join(tenant_name, "tenant_documents", filename)


# =====================================================================
# 1. Core Tenant, TenantOperation, Organization
# =====================================================================

class Tenant(UUIDModel, TimeStampedModel):
    """The master record for a company using the platform. Every other
    tenant-owned table ultimately points back here."""

    class WorkspaceType(models.TextChoices):
        # sheet 16: tenant.workspace_type — is this a real company, or just
        # one person's personal workspace (no organisational privileges)?
        ORGANISATION = "ORGANISATION", "Organisation tenant"
        PERSONAL = "PERSONAL", "Personal workspace"

    class OrganisationType(models.TextChoices):
        # sheet 16: tenant.organisation_type — controls which pathways and
        # permissions this tenant gets.
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
        # sheet 16: tenant.account_status — overall lifecycle state.
        # PENDING is the default: unverified until TenantVerification approves it.
        # Role note (sheet 17): transitioning TO SUSPENDED requires Super Admin specifically
        # (TENANT_SUSPEND), not generic Platform Admin. TO CLOSED requires Super Admin/Legal/
        # Billing jointly (TENANT_CLOSE). TO ARCHIVED is Platform Admin. Enforce at the API/
        # permission layer — the field itself doesn't encode who can set it.
        PENDING = "PENDING", "Pending"
        ACTIVE = "ACTIVE", "Active"
        RESTRICTED = "RESTRICTED", "Restricted"
        SUSPENDED = "SUSPENDED", "Suspended"
        ARCHIVED = "ARCHIVED", "Archived"
        CLOSED = "CLOSED", "Closed"

    # --- System Identity ---
    name = models.CharField(
        max_length=200, validators=[MinLengthValidator(2)],
        help_text="Tenant display name.",
    )  # Internal display name used across the platform UI.

    code = models.CharField(
        max_length=50, unique=True, validators=[validate_uppercase_code],
        help_text="tenant.tenant_code — stable internal reference, never the company name.",
    )  # sheet 16: tenant.tenant_code. Human-readable reference like QTN-000123. Never changes, even if the company renames itself.

    workspace_type = models.CharField(
        max_length=20, choices=WorkspaceType.choices,
        help_text="tenant.workspace_type — personal workspaces get no organisational privileges.",
    )  # sheet 16: tenant.workspace_type. Set once at creation.

    # --- Organisation Identity ---
    legal_name = models.CharField(
        max_length=250, blank=True,
        help_text="Registered legal name, when different from display name.",
    )  # sheet 16: tenant.legal_name. The company's official registered name — comes from registration evidence.

    trade_name = models.CharField(max_length=200, blank=True)
    # sheet 16: tenant.trade_name. The name they actually go by day-to-day, if different from the legal name.

    organisation_type = models.CharField(max_length=30, choices=OrganisationType.choices)
    # sheet 16: tenant.organisation_type. Self-declared at application, may be corrected by the reviewer.

    parent_tenant = models.ForeignKey(
        "self", on_delete=models.PROTECT, null=True, blank=True, related_name="child_tenants",
        help_text="tenant.parent_tenant_id — group hierarchy.",
    )  # sheet 16: tenant.parent_tenant_id. If this tenant is part of a bigger group, which tenant owns it. Platform Admin sets this, not the tenant itself.

    description = models.TextField(blank=True, help_text="Max 2000 chars per blueprint.")
    # sheet 16: tenant.description. A short "about us" paragraph.

    website = models.URLField(max_length=500, blank=True)
    # sheet 16: tenant.website. Verified against domain/website ownership where possible.

    # --- Industry / Service Profile ---
    # Both fields below are sheet 16 "Enum list" type with Repeatable=No — the sheet's own
    # Database Path column specifies them as plain array columns directly on tenants (tenants.
    # industry_ids[], tenants.service_scope_ids[]), NOT as separate "Repeatable record" tables
    # like tax_registrations or authorised_representatives are. Each is a flat list of codes,
    # validated against the relevant lookup table (catalog.ReferenceValue / catalog.ScopeCatalog)
    # at the serializer/service layer — same pattern professional_profiles.additional_role_codes
    # already uses elsewhere in this codebase, not enforced via a join table.

    industry_ids = models.JSONField(default=list, blank=True, help_text="tenant.industry_ids — list of catalog.ReferenceValue codes (option_type=INDUSTRY).")
    # sheet 16: tenant.industry_ids. Required field. What industries the tenant declares serving —
    # filters which modules/projects the tenant sees. NOT the same as TenantOperation, which is a
    # per-country registration permission (different table, different purpose — see its docstring).

    service_scope_ids = models.JSONField(default=list, blank=True, help_text="tenant.service_scope_ids — list of catalog.ScopeCatalog codes.")
    # sheet 16: tenant.service_scope_ids. Optional. Which specific scopes/services the tenant offers.

    # --- Platform access (pre-existing, not in the blueprint but required for the app to function) ---
    portal_slug = models.SlugField(max_length=80, unique=True, validators=[validate_lowercase_slug])
    # The URL segment this tenant's users log in through, e.g. qualion.com/<slug>/login.

    custom_domain = models.CharField(max_length=255, unique=True, null=True, blank=True)
    # Optional white-labelled domain the tenant can use instead of the shared portal_slug URL.

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    # sheet 16: tenant.account_status. See Status choices above for what each value means.

    registration_enabled = models.BooleanField(default=True)
    # Kill switch: when false, this tenant's registration endpoint rejects new sign-ups even if status=ACTIVE.

    login_enabled = models.BooleanField(default=True)
    # Kill switch: when false, nobody can log into this tenant, even if status=ACTIVE. Used for emergency lockouts.

    default_timezone = models.CharField(max_length=64, validators=[validate_iana_timezone])
    # sheet 16: tenant.default_time_zone. IANA timezone string, e.g. "Asia/Kolkata". Drives scheduling/logs.

    default_currency = models.CharField(max_length=3, validators=[validate_iso_currency_code])
    # sheet 16: tenant.default_currency. ISO 4217 code, e.g. "USD". Used across all commercial fields.

    contact_email = models.EmailField(max_length=254, blank=True)
    # General-purpose contact email for the tenant as a whole (distinct from the specific TenantContact rows).

    contact_phone = models.CharField(max_length=20, blank=True, validators=[validate_e164_phone])
    # General-purpose contact phone, E.164 format.

    settings = models.JSONField(default=dict, blank=True)
    # Free-form feature-flag bag for platform-internal use — not part of the sheet 16 field list.

    branding = models.JSONField(default=dict, blank=True)
    # Legacy/simple branding cache — TenantBranding (section 9) is the structured, authoritative version.

    logo = models.ImageField(
        upload_to=tenant_logo_upload_path, max_length=1000, null=True, blank=True,
        validators=[MaxFileSizeValidator(MAX_TENANT_LOGO_SIZE_BYTES)],
    )  # sheet 16: tenant.logo. Kept on Tenant itself (not moved into TenantBranding) since it existed here originally.

    # --- Status & Audit ---
    status_reason = models.TextField(
        blank=True,
        help_text="Required when status changes to RESTRICTED/SUSPENDED/ARCHIVED/CLOSED — enforce in serializer/service layer.",
    )  # sheet 16: tenant.status_reason. Why the status last changed. Filled by whoever's authorised to make that change.

    created_by = models.ForeignKey("accounts.UserTbl", on_delete=models.PROTECT, related_name="tenants_created")
    # sheet 16: tenant.created_by. The founding UserTbl row is created in the SAME request as this
    # Tenant row (TENANT_SUBMIT) — accounts.UserTbl.tenant is required, so the user can't exist
    # before this tenant does. See TenantVerification for the approval sequencing that activates
    # this account once both the tenant and the user are approved.
    # sheet 16: tenant.created_by. System-stamped — whichever platform user's action created this row.

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
        # Normalise casing on save so lookups/uniqueness checks are consistent.
        if self.contact_email:
            self.contact_email = self.contact_email.lower()
        if self.portal_slug:
            self.portal_slug = self.portal_slug.lower()
        if self.custom_domain:
            self.custom_domain = self.custom_domain.lower()
        super().save(*args, **kwargs)


class TenantOperation(TimeStampedModel):
    """Industry + country combination the tenant is permitted to operate
    and register candidates in. Distinct from Tenant.industry_ids: that
    field is the tenant's own self-declared profile (what industries it
    works in, shown on its own dashboard). This table is the platform's
    grant of actual candidate-registration permission for a specific
    industry + country pair — a compliance checkpoint, not a profile fact.

    Request/approve, the same shape TenantVerification uses. The
    tenant's Organisation Admin requests an operating permission;
    Platform Admin approves or rejects it before is_registration_enabled
    can take effect. This keeps the tenant in control of declaring its
    own footprint while preserving the platform's compliance checkpoint
    before candidate registration opens in a given jurisdiction.

    At least one row is required at TENANT_SUBMIT time — the reviewer
    approving a tenant's legitimacy must always have visibility into
    where it intends to operate. Requests made after the tenant is
    already active (genuine expansion into a new country) are a
    separate, standalone flow; only the initial submission requires it."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending Approval"
        ACTIVE = "ACTIVE", "Active"
        REJECTED = "REJECTED", "Rejected"
        SUSPENDED = "SUSPENDED", "Suspended"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="operations", db_index=True)
    # Which tenant this operating permission belongs to. CASCADE here (not PROTECT) is a deliberate, documented
    # exception — see core/models.py's TenantOwnedModel docstring.

    industry = models.ForeignKey("catalog.ReferenceValue", on_delete=models.PROTECT, related_name="tenant_operations", db_index=True)
    # Which industry (from the shared lookup table) this row declares. Same table Organization.industry uses.

    country_code = models.CharField(max_length=2, validators=[validate_iso_country_code])
    # Required — every operating permission is a specific industry+country pair.

    region_name = models.CharField(max_length=120, blank=True)
    # Optional state/province/region qualifier within the country.

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    # The approval state of this specific request. Registration cannot actually be enabled
    # (see is_registration_enabled below) until this reaches ACTIVE.

    is_registration_enabled = models.BooleanField(
        default=True,
        help_text="Only takes effect once status=ACTIVE. Lets the tenant pause/resume registration in an already-approved industry+country without re-requesting approval.",
    )  # Only operations with this set to True AND status=ACTIVE appear as options during candidate/user registration.

    is_active = models.BooleanField(default=True)
    # General on/off switch, independent of both status and is_registration_enabled — e.g. archiving an old, no-longer-relevant operation.

    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    # Optional validity window for this operating permission.

    requested_by = models.ForeignKey(
        "accounts.UserTbl", on_delete=models.PROTECT, related_name="tenant_operations_requested",
    )  # The tenant's own Organisation Admin — NOT Platform Super Admin. This is the field that
    # was previously named `created_by` with an incorrect "must be Platform Super Admin" rule.

    reviewed_by = models.ForeignKey(
        "accounts.UserTbl", on_delete=models.SET_NULL, null=True, blank=True, related_name="tenant_operations_reviewed",
    )  # Platform Admin who approved/rejected the request. Null until reviewed.

    reviewed_at = models.DateTimeField(null=True, blank=True)
    # When the review decision was made.

    rejection_reason = models.TextField(blank=True)
    # Required when status=REJECTED — same accountability pattern as TenantVerification.reason.

    class Meta:
        db_table = "tenancy_tenant_operation"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "industry", "country_code"], name="uniq_tenant_operation_tenant_industry_country"),
            models.CheckConstraint(
                check=Q(effective_from__isnull=True) | Q(effective_to__isnull=True) | Q(effective_from__lte=F("effective_to")),
                name="chk_tenant_operation_dates",
            ),  # effective_from must not be after effective_to, when both are set.
        ]


class Organization(UUIDModel, TimeStampedModel):
    """Covers TWO conceptually different things through one discriminator
    field (organization_type): external business relationships (clients,
    employers, colleges) AND the tenant's own internal structure
    (branches, departments, operating units). Referenced by
    resumes.ResumeTemplate.client_organization and
    experience.ProfessionalAssignment.organization — do not remove or
    rename existing fields on this model.

    Role note (sheet 17): creating rows here (BUSINESS_UNIT_ADD) is
    plain Organisation Admin self-serve, no review needed. Merging two
    duplicate rows (ORG_MERGE) is Super Admin specifically — a more
    restricted role than general Platform Admin. No schema change for
    merge; log it via governance.AuditEvent (action=MERGE_DUPLICATE)
    with the permission check enforced at the API layer."""

    class OrganizationType(models.TextChoices):
        # The first three are "internal structure" types — see INTERNAL_STRUCTURE_TYPES below.
        BRANCH = "BRANCH", "Branch"
        DEPARTMENT = "DEPARTMENT", "Department"
        OPERATING_UNIT = "OPERATING_UNIT", "Operating unit"
        # Everything below this line is an external party, not part of the tenant itself.
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

    # Used by TenantLocation.business_unit and Project.business_unit to restrict which
    # Organization rows are valid "internal structure" references.
    INTERNAL_STRUCTURE_TYPES = (OrganizationType.BRANCH, OrganizationType.DEPARTMENT, OrganizationType.OPERATING_UNIT)

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="organizations", db_index=True)
    # Which tenant owns this organisation record. CASCADE is a documented exception, same as TenantOperation.

    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True, related_name="children")
    # Enables a real hierarchy — e.g. a Branch under a Department under an Operating Unit.

    organization_type = models.CharField(max_length=40, choices=OrganizationType.choices)
    # The discriminator that decides which "kind" of Organization row this is.

    name = models.CharField(max_length=200, validators=[MinLengthValidator(2)])
    # Display name — the branch/department/client's name.

    legal_name = models.CharField(max_length=250, blank=True)
    # Legal name, if different from the display name (mainly relevant for external orgs like clients).

    code = models.CharField(max_length=60, blank=True, null=True)
    # Optional tenant-specific short code, must be unique within the tenant when set (see constraint below).

    industry = models.ForeignKey("catalog.ReferenceValue", on_delete=models.PROTECT, null=True, blank=True, related_name="organizations")
    # Which industry this organisation is primarily associated with, if relevant.

    country_code = models.CharField(max_length=2, blank=True, validators=[validate_iso_country_code])
    city = models.CharField(max_length=120, blank=True)
    # Basic location info — not a full structured address (see TenantLocation for that).

    website = models.URLField(max_length=500, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    # Contact info for this organisation.

    external_reference = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    # ID from an external system this record was imported from, if any.

    metadata = models.JSONField(default=dict, blank=True)
    # Free-form extra attributes that don't warrant their own column.

    is_active = models.BooleanField(default=True)
    # Inactive rows can't be selected for new assignments (projects, locations, etc.) but stay for history.

    # --- Internal-structure fields (branches/departments/operating units) ---
    owner = models.ForeignKey(
        "accounts.UserTbl", on_delete=models.PROTECT, null=True, blank=True, related_name="owned_organizations",
        help_text="Required in practice for BRANCH/DEPARTMENT/OPERATING_UNIT rows (sheet 19 tenant_business_units.owner); optional for external org types.",
    )  # Who's accountable for this division. Required by clean() below when organization_type is an internal structure type.

    legal_entity = models.ForeignKey(
        "TenantLegalEntity", on_delete=models.SET_NULL, null=True, blank=True, related_name="business_units",
        help_text="Which legal entity this internal division sits under, if applicable.",
    )  # Optional link — which of the tenant's legal entities (section 2) this division belongs to.

    class Meta:
        db_table = "tenancy_organization"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], condition=Q(code__isnull=False), name="uniq_organization_tenant_code"),
        ]

    def clean(self):
        super().clean()
        if self.parent_id and self.parent_id == self.id:
            raise ValidationError({"parent": "Organization cannot be its own parent."})
        if self.organization_type in self.INTERNAL_STRUCTURE_TYPES and self.owner_id is None:
            raise ValidationError({"owner": "Branch/Department/Operating unit rows require an owner."})

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)


# =====================================================================
# 2. Legal Registration
# =====================================================================

class TenantLegalEntity(UUIDModel, TenantOwnedModel, TimeStampedModel):
    """One row per legal company beneath the tenant — a tenant can own
    several subsidiaries, each added via LEGAL_ENTITY_ADD.

    Sheet 17 specifies LEGAL_ENTITY_ADD as a dual-party operation
    (Organisation Admin + Platform Reviewer), not Org Admin self-serve.
    The tenant's own founding legal entity, submitted with the initial
    application, is approved implicitly the moment the tenant itself is
    approved — same reviewer, same transaction, no separate action
    needed. Any legal entity added after the tenant is already active
    (a new subsidiary) needs its own explicit Platform Reviewer
    decision, using the same request/approve shape as TenantOperation."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending Approval"
        ACTIVE = "ACTIVE", "Active"
        REJECTED = "REJECTED", "Rejected"

    registration_number = EncryptedCharField(
        max_length=100, help_text="Restricted PII/Legal per sheet 16 — encrypted at rest.",
    )  # sheet 16: tenant.registration_number. Encrypted because it's Restricted PII/Legal classification.

    country_of_incorporation = models.CharField(max_length=2, validators=[validate_iso_country_code])
    # sheet 16: tenant.country_of_incorporation. Sets the legal jurisdiction.

    incorporation_date = models.DateField(null=True, blank=True)
    # sheet 16: tenant.incorporation_date. When the company was founded.

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    # PENDING at creation always — including the founding entity submitted with the initial
    # application. Flipped to ACTIVE either automatically (founding entity, at TENANT_APPROVE
    # time) or via explicit review (any entity added afterward).

    requested_by = models.ForeignKey("accounts.UserTbl", on_delete=models.PROTECT, related_name="legal_entities_requested")
    # The Organisation Admin who added this entity — for the founding entity, this is the applicant.

    reviewed_by = models.ForeignKey("accounts.UserTbl", on_delete=models.SET_NULL, null=True, blank=True, related_name="legal_entities_reviewed")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    # Who approved/rejected it and when. For the founding entity, set automatically to match
    # the TenantVerification decision — never left blank just because no separate review UI ran.

    rejection_reason = models.TextField(blank=True)
    # Required when status=REJECTED.

    class Meta:
        db_table = "tenancy_tenant_legal_entity"


class TenantTaxRegistration(UUIDModel, TenantOwnedModel, TimeStampedModel):
    """One row per tax registration (a legal entity can have several,
    e.g. GST + a separate export registration)."""

    class TaxType(models.TextChoices):
        GST = "GST", "GST"
        VAT = "VAT", "VAT"
        TAX_ID = "TAX_ID", "Tax ID"

    legal_entity = models.ForeignKey(TenantLegalEntity, on_delete=models.CASCADE, related_name="tax_registrations")
    # Which legal entity this tax registration belongs to.

    tax_type = models.CharField(max_length=20, choices=TaxType.choices)
    # Which kind of tax registration this is.

    country_code = models.CharField(max_length=2, validators=[validate_iso_country_code])
    # Which country this registration applies in.

    tax_number = EncryptedCharField(
        max_length=100, help_text="Encrypted at rest — same classification as TenantLegalEntity.registration_number.",
    )  # sheet 16: part of tenant.tax_registrations. Encrypted, same reasoning as registration_number above.

    status = models.CharField(max_length=20, default="ACTIVE")
    # Whether this specific tax registration is currently valid.

    class Meta:
        db_table = "tenancy_tenant_tax_registration"


class TenantDomain(UUIDModel, TenantOwnedModel, TimeStampedModel):
    """A verified email domain (e.g. @acmecorp.com) that controls who can
    join this tenant automatically and whether SSO is offered."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        VERIFIED = "VERIFIED", "Verified"
        FAILED = "FAILED", "Failed"

    domain = models.CharField(max_length=255)
    # sheet 16: tenant.verified_email_domains. The domain itself, e.g. "acmecorp.com".

    verification_status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    # Result of the DNS/email verification check.

    verified_at = models.DateTimeField(null=True, blank=True)
    # When verification succeeded, if it has.

    class Meta:
        db_table = "tenancy_tenant_domain"
        constraints = [models.UniqueConstraint(fields=["tenant", "domain"], name="uniq_tenant_domain")]


# =====================================================================
# 3. Locations (section 3 previously held TenantScope, a separate
#    relational table for service_scope_ids — removed on recheck: sheet
#    16 marks that field "Enum list"/Repeatable=No, meaning it belongs
#    as a plain array column directly on Tenant, not its own table.
#    See Tenant.service_scope_ids above.)
# =====================================================================
# =====================================================================

class TenantLocation(UUIDModel, TenantOwnedModel, TimeStampedModel):
    """Every physical address the tenant has — registered office,
    billing address, branches, yards, everything with a real street
    address, all in one table via the location_type discriminator."""

    class LocationType(models.TextChoices):
        REGISTERED = "REGISTERED", "Registered office"
        CORPORATE = "CORPORATE", "Corporate office"
        BILLING = "BILLING", "Billing address"
        BRANCH = "BRANCH", "Branch"
        PROJECT_OFFICE = "PROJECT_OFFICE", "Project office"
        FACTORY = "FACTORY", "Factory"
        YARD = "YARD", "Yard"
        PORT_SITE = "PORT_SITE", "Port site"

    business_unit = models.ForeignKey(
        Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name="locations",
        help_text="Must be an Organization row with organization_type in BRANCH/DEPARTMENT/OPERATING_UNIT — enforce in clean().",
    )  # Optional link to which internal division this location belongs to.

    location_type = models.CharField(max_length=20, choices=LocationType.choices)
    # Which kind of address this is — see sheet 16 fields: registered_address, corporate_address,
    # billing_address, operating_locations all map to different location_type values here.

    location_code = models.CharField(max_length=100, blank=True)
    # Optional short reference code for this location, unique within the tenant when set.

    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country_code = models.CharField(max_length=2, validators=[validate_iso_country_code])
    # Standard structured address fields.

    timezone = models.CharField(max_length=64, validators=[validate_iana_timezone])
    # sheet 16: tenant.default_time_zone is on Tenant itself, but each individual location can have its own.

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # Optional map coordinates, e.g. for a remote yard/port site.

    is_head_office = models.BooleanField(default=False)
    is_default_billing = models.BooleanField(default=False)
    is_default_project_location = models.BooleanField(default=False)
    # Convenience flags so the app can quickly find "the" default address of each kind without a type lookup.

    is_active = models.BooleanField(default=True)
    # Deactivated locations can't be selected for new projects but stay for history.

    class Meta:
        db_table = "tenancy_tenant_location"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "location_code"],
                condition=Q(location_code__isnull=False) & ~Q(location_code=""),
                name="uniq_location_code_per_tenant",
            ),
        ]

    def clean(self):
        super().clean()
        if self.business_unit_id and self.business_unit.organization_type not in Organization.INTERNAL_STRUCTURE_TYPES:
            raise ValidationError({"business_unit": "Must reference a BRANCH/DEPARTMENT/OPERATING_UNIT Organization row."})

    def __str__(self):
        return f"{self.tenant} — {self.get_location_type_display()}"


# =====================================================================
# 4. Authorised Representatives & Contacts
# =====================================================================

class TenantAuthorisedRepresentative(UUIDModel, TenantOwnedModel, TimeStampedModel):
    """The legally authorised person(s) who can approve onboarding and
    major changes on behalf of the company — e.g. a director. At least
    one active, verified row is required for the tenant to be approved."""

    class AuthorityType(models.TextChoices):
        DIRECTOR = "DIRECTOR", "Director"
        POWER_OF_ATTORNEY = "POWER_OF_ATTORNEY", "Power of Attorney"
        DESIGNATED_SIGNATORY = "DESIGNATED_SIGNATORY", "Designated Signatory"

    user = models.ForeignKey("accounts.UserTbl", on_delete=models.SET_NULL, null=True, blank=True, related_name="representative_of")
    # Linked platform user account, if this representative also has a login.

    full_name = models.CharField(max_length=255)
    title = models.CharField(max_length=100, blank=True)
    official_email = models.EmailField()
    mobile = models.CharField(max_length=20, validators=[validate_e164_phone])
    # sheet 16: tenant.authorised_representatives — name, title, official email, mobile.

    authority_type = models.CharField(max_length=30, choices=AuthorityType.choices)
    # What kind of legal authority this person holds.

    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    # Validity window for this person's authority.

    verification_status = models.CharField(max_length=30, choices=VerificationStatus.choices, default=VerificationStatus.SELF_DECLARED)
    # Reuses the platform's shared verification vocabulary rather than a new enum.

    evidence_document = models.ForeignKey(
        "TenantDocument", on_delete=models.SET_NULL, null=True, blank=True, related_name="representative_proofs",
    )  # sheet 16: tenant.authority_document. The uploaded proof (board resolution, POA, etc.).

    class Meta:
        db_table = "tenancy_tenant_authorised_representative"


class TenantContact(UUIDModel, TenantOwnedModel, TimeStampedModel):
    """The tenant's day-to-day points of contact — distinct from the
    Authorised Representative above, who has legal authority but isn't
    necessarily who you'd actually call about a technical issue."""

    class ContactType(models.TextChoices):
        ORG_ADMIN = "ORG_ADMIN", "Organisation Admin"
        TECHNICAL = "TECHNICAL", "Technical"
        PROJECT = "PROJECT", "Project"
        FINANCE = "FINANCE", "Finance"
        LEGAL = "LEGAL", "Legal"
        SECURITY = "SECURITY", "Security"

    contact_type = models.CharField(max_length=20, choices=ContactType.choices)
    # sheet 16 has 6 separate contact fields (organisation_admin_contact, technical_contact, etc.) —
    # all consolidated into this one table via this discriminator, instead of 6 separate FK fields on Tenant.

    user = models.ForeignKey("accounts.UserTbl", on_delete=models.SET_NULL, null=True, blank=True, related_name="tenant_contact_roles")
    # Linked platform user, if this contact is also a tenant member.

    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    # Contact details, usable even if there's no linked user account.

    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    # Validity window — e.g. if the finance contact changes, keep the old row for history.

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "tenancy_tenant_contact"


# =====================================================================
# 5. Verification & Documents
# =====================================================================

class TenantVerification(TenantOwnedModel, CreatedOnlyModel):
    """The tenant's approval history. Append-only — every status change
    inserts a NEW row here, never updates an old one in place, so the
    full decision history is always preserved (same pattern as
    CompetencyAssessment elsewhere in the platform).

    Business rule (app-layer, not enforced by this schema — there's no
    clean DB constraint for "at least one related row exists"): the
    submission flow (TENANT_SUBMIT) must require at least one
    TenantOperation request before accepting the application at all.
    Without this, a reviewer could approve a tenant having seen zero
    information about where it intends to operate — which defeats the
    point of a reviewer looking at it in the first place. Enforce this
    as a 400 at the API layer on the submit endpoint, not here."""

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
    # sheet 16: tenant.verification_status. Current state of this specific review cycle.

    submitted_at = models.DateTimeField(null=True, blank=True)
    # sheet 16: tenant.verification_submitted_at. System-stamped the moment the application is submitted.

    reviewed_by = models.ForeignKey("accounts.UserTbl", on_delete=models.SET_NULL, null=True, blank=True, related_name="tenant_reviews_done")
    # sheet 16: tenant.reviewed_by. Which Platform Reviewer made the decision.

    reviewed_at = models.DateTimeField(null=True, blank=True)
    # sheet 16: tenant.reviewed_at. When they made it.

    reason = models.TextField(blank=True)
    # sheet 16: tenant.review_decision_reason. Why — required for return/reject decisions.

    risk_classification = models.CharField(max_length=20, choices=RiskClassification.choices, default=RiskClassification.STANDARD)
    # sheet 16: tenant.risk_classification. Determines how much ongoing scrutiny this tenant needs.

    next_review_date = models.DateField(null=True, blank=True)
    # sheet 16: tenant.periodic_review_date. When this tenant needs to be re-checked.

    class Meta:
        db_table = "tenancy_tenant_verification"
        ordering = ["-created_at"]


class TenantDocument(UUIDModel, TenantOwnedModel, TimeStampedModel, ArchivableModel):
    """Every proof file supporting the tenant's legal/verification claims
    — registration certs, tax certs, address proof, authority letters."""

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
    # What kind of proof this file is.

    file = models.FileField(
        upload_to=tenant_document_upload_path, max_length=1000, validators=[MaxFileSizeValidator(MAX_TENANT_LOGO_SIZE_BYTES)],
    )  # The actual uploaded file.

    file_hash = models.CharField(max_length=128)
    # Integrity hash of the stored file — lets you detect if a file was tampered with.

    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    # When the underlying document was issued / expires, if applicable.

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    # Current state of this specific document.

    reviewed_by = models.ForeignKey("accounts.UserTbl", on_delete=models.SET_NULL, null=True, blank=True, related_name="tenant_documents_reviewed")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    # Who reviewed this document and when, if it's gone through review.

    remarks = models.TextField(blank=True)
    # Free-text notes from the reviewer.

    superseded_by = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="supersedes")
    # If a newer version of this document was uploaded, points to it — old evidence is never deleted, only superseded.

    class Meta:
        db_table = "tenancy_tenant_document"


# =====================================================================
# 6. Legal, Confidentiality & Settings
# =====================================================================

class TenantLegalAcceptance(TenantOwnedModel, CreatedOnlyModel):
    """Records of the tenant agreeing to platform terms or the data
    processing agreement. See the discriminator field below — the two
    types have very different real-world workflows even though they
    share a table shape."""

    class AcceptanceType(models.TextChoices):
        TERMS = "TERMS", "Platform Terms"
        # sheet 16: tenant.terms_acceptance. Source="System" — this is a simple, self-serve
        # click-to-accept during onboarding. The system logs it automatically.
        DPA = "DPA", "Data Processing Terms"
        # sheet 16: tenant.data_processing_terms. Source="Legal workflow" — this is NOT
        # self-serve. Only required "where applicable" (e.g. cross-border data transfer),
        # and routed through the Legal Contact before being recorded here.

    acceptance_type = models.CharField(max_length=10, choices=AcceptanceType.choices)
    version = models.CharField(max_length=50)
    # Which version of the terms/DPA was accepted — matters because terms change over time.

    accepted_by = models.ForeignKey("accounts.UserTbl", on_delete=models.PROTECT, related_name="tenant_acceptances")
    # WHO clicked accept / whose legal sign-off this represents. This is the field that answers
    # "who filled this in" — it's always a specific person, recorded automatically at the moment of acceptance.

    jurisdiction = models.CharField(max_length=100, blank=True)
    # Relevant mainly for DPA rows — which legal jurisdiction's terms apply.

    class Meta:
        db_table = "tenancy_tenant_legal_acceptance"


class TenantLegalSettings(TenantOwnedModel):
    """One row per tenant (1:1) — kept as its own table, separate from
    Tenant itself, so it can carry stricter Restricted/Legal access
    control than the rest of the tenant record."""

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
    # One-to-one — every tenant has exactly one of these rows.

    nda_requirement = models.CharField(max_length=20, choices=NdaRequirement.choices, default=NdaRequirement.NOT_REQUIRED)
    # sheet 16: tenant.nda_requirement. Whether a disclosure request needs an NDA first.

    default_classification = models.CharField(max_length=20, choices=Classification.choices, default=Classification.INTERNAL)
    # sheet 16: tenant.confidentiality_classification. Default sensitivity applied to this tenant's data.

    retention_policy = models.CharField(max_length=100, blank=True)
    # sheet 16: tenant.data_retention_policy. How long data is kept before archive/delete.

    is_legal_hold = models.BooleanField(
        default=False, help_text="Blocks retention/deletion jobs while true — RETENTION_APPLY must check this first.",
    )  # Not in sheet 16 directly, but required by the RETENTION_APPLY operation in sheet 17 ("approved policy
    # and hold checks") — a legal hold must be able to override normal retention/deletion.

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenancy_tenant_legal_settings"


class TenantNda(TenantOwnedModel, CreatedOnlyModel):
    """One row per actual signed NDA document — a tenant can have
    several over time (renewals, project-specific ones, etc.)."""

    version = models.CharField(max_length=50)
    parties = models.JSONField(default=list)
    signatories = models.JSONField(default=list)
    # sheet 16: tenant.nda_records — version, parties, signatories.

    effective_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    # Validity window of this specific NDA.

    evidence_document = models.ForeignKey(TenantDocument, on_delete=models.SET_NULL, null=True, blank=True, related_name="ndas")
    # The actual signed file.

    class Meta:
        db_table = "tenancy_tenant_nda"


class TenantSettings(TenantOwnedModel):
    """1:1 with tenant. Note: timezone and currency stay on Tenant itself
    (sheet 16's Database Path points them there directly) — this table
    is only for the remaining localisation fields sheet 19 lists as a
    separate object."""

    tenant = models.OneToOneField(Tenant, on_delete=models.PROTECT, related_name="settings")

    default_language = models.CharField(max_length=10, default="en")
    # sheet 16: tenant.default_language.

    date_format = models.CharField(max_length=20, default="DD-MM-YYYY")
    number_format = models.CharField(max_length=20, default="1,234.56")
    # sheet 16: tenant.date_format / tenant.number_format. Pure display formatting, no business logic.

    measurement_system = models.CharField(
        max_length=10, choices=[("METRIC", "Metric"), ("IMPERIAL", "Imperial"), ("MIXED", "Mixed")], default="METRIC",
    )  # sheet 16: tenant.measurement_system. Affects inspection forms and reports.

    working_calendar = models.CharField(max_length=100, blank=True)
    # sheet 16: tenant.working_calendar. Which holiday/working-day calendar applies for scheduling.

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenancy_tenant_settings"


# =====================================================================
# 7. Subscription & Modules
# =====================================================================

class TenantSubscription(TenantOwnedModel, TimeStampedModel):
    """What the tenant is paying for. Versioned — insert a NEW row every
    time the plan changes, never edit an old one in place, so there's a
    full history of what entitlements applied when."""

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
    # sheet 16: tenant.subscription_plan.

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TRIAL)
    # sheet 16: tenant.subscription_status. Controls whether paid functionality is actually active.

    start_date = models.DateField()
    renewal_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    # sheet 16: tenant.subscription_dates.

    seat_limit = models.PositiveIntegerField()
    # sheet 16: tenant.seat_limit. How many members the tenant can have.

    project_limit = models.PositiveIntegerField(null=True, blank=True)
    # sheet 16: tenant.project_limit.

    storage_limit_gb = models.PositiveIntegerField(null=True, blank=True)
    # sheet 16: tenant.storage_limit.

    used_seats = models.PositiveIntegerField(default=0)
    used_projects = models.PositiveIntegerField(default=0)
    used_storage_gb = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Not in sheet 16 directly — running usage counters so the app can enforce the limits above
    # without re-counting every related table on every request.

    class Meta:
        db_table = "tenancy_tenant_subscription"
        ordering = ["-created_at"]


class Module(TimeStampedModel):
    """Platform-level feature modules (SMS, LPMS, TPI, AUDIT,
    RESUME_BUILDER). No tenant FK — this is a shared master list, same
    idea as the ReferenceValue lookup table."""

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "tenancy_module"

    def __str__(self):
        return self.code


class TenantModuleEntitlement(TenantOwnedModel, TimeStampedModel):
    """Which modules THIS tenant specifically has access to."""

    module = models.ForeignKey(Module, on_delete=models.PROTECT, related_name="tenant_entitlements")
    # sheet 16: tenant.enabled_modules — one row per enabled module.

    status = models.CharField(max_length=20, default="ACTIVE")
    limits = models.JSONField(default=dict, blank=True)
    # Any module-specific usage limits.

    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    # Validity window for this specific entitlement.

    class Meta:
        db_table = "tenancy_tenant_module_entitlement"
        constraints = [models.UniqueConstraint(fields=["tenant", "module"], name="uniq_tenant_module")]


# =====================================================================
# 8. Branding & Templates
# =====================================================================

class TenantBranding(TenantOwnedModel):
    """1:1 with tenant — the tenant's branded-output configuration."""

    tenant = models.OneToOneField(Tenant, on_delete=models.PROTECT, related_name="branding")

    logo = models.ImageField(
        upload_to="tenant_branding/logos/", max_length=1000, null=True, blank=True,
        validators=[MaxFileSizeValidator(MAX_TENANT_LOGO_SIZE_BYTES)],
    )  # A second logo slot, specifically for branded document output (Tenant.logo above is the account-level one).

    colours = models.JSONField(default=dict, blank=True)
    # sheet 16: tenant.brand_colours.

    report_header = models.TextField(blank=True)
    report_footer = models.TextField(blank=True)
    # sheet 16: tenant.report_header_footer, split into two fields.

    disclaimer_text = models.TextField(blank=True)
    # sheet 16: tenant.disclaimer_text. Legal footer text on generated documents.

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenancy_tenant_branding"


class TenantReportTemplate(TenantOwnedModel, TimeStampedModel):
    """Templates for inspection/project reports. No equivalent model
    exists elsewhere in the codebase for this concept — genuinely
    needed, unlike resume templates (see resumes.ResumeTemplate)."""

    template_name = models.CharField(max_length=255)
    file = models.FileField(upload_to="tenant_templates/report/", max_length=1000)
    version = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default="DRAFT")
    # sheet 16: tenant.report_templates.

    reviewed_by = models.ForeignKey("accounts.UserTbl", on_delete=models.SET_NULL, null=True, blank=True, related_name="report_templates_reviewed")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    # REPORT_TEMPLATE_MANAGE (sheet 17) names Technical Reviewer / Template Admin as the
    # approver — these fields record who actually approved a given version, and when.

    approval_matrix = models.JSONField(default=list, blank=True)
    # Which roles must sign off before this specific template version is released — per-template override
    # of the tenant-wide default in TenantApprovalMatrix (section 14).

    class Meta:
        db_table = "tenancy_tenant_report_template"


# =====================================================================
# 9. Security
# =====================================================================

class TenantSecuritySettings(TenantOwnedModel):
    """1:1 with tenant — how strictly this tenant's account is locked
    down. Platform sets the floor; the tenant can tighten but never
    weaken below it."""

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
    # sheet 16: tenant.mfa_policy.

    sso_status = models.CharField(max_length=15, choices=SsoStatus.choices, default=SsoStatus.DISABLED)
    identity_provider = models.CharField(max_length=100, blank=True)
    # sheet 16: tenant.sso_status / tenant.identity_provider.

    session_policy = models.JSONField(default=dict, blank=True)
    # sheet 16: tenant.session_policy. E.g. session timeout rules.

    api_access_status = models.CharField(max_length=15, choices=ApiAccessStatus.choices, default=ApiAccessStatus.DISABLED)
    # sheet 16: tenant.api_access_status.

    export_policy = models.JSONField(default=dict, blank=True)
    # sheet 16: tenant.export_policy. What data can be downloaded.

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenancy_tenant_security_settings"


class TenantIPRestriction(UUIDModel):
    """One row per allowed IP range — a tenant can have several (head
    office + a couple of site offices, say)."""

    security_settings = models.ForeignKey(TenantSecuritySettings, on_delete=models.CASCADE, related_name="ip_restrictions")
    cidr_range = models.CharField(max_length=100)
    # sheet 16: tenant.ip_restrictions. A CIDR block, e.g. "203.0.113.0/24".

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tenancy_tenant_ip_restriction"


class TenantIntegration(TenantOwnedModel, TimeStampedModel):
    """External systems connected to this tenant, and their credentials."""

    integration_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default="ACTIVE")
    # sheet 16: tenant.integration_credentials — type and status.

    secret_reference = EncryptedCharField(max_length=255, help_text="Never exported; encrypted at rest.")
    # The actual secret/API key, encrypted — never appears in plain-text exports or logs.

    scopes = models.JSONField(default=list, blank=True)
    # What this integration is allowed to access.

    rotated_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    # When the credential was last rotated / when it expires.

    class Meta:
        db_table = "tenancy_tenant_integration"


# =====================================================================
# 10. Billing
# =====================================================================

class TenantBilling(TenantOwnedModel):
    """1:1 with tenant — invoicing configuration."""

    tenant = models.OneToOneField(Tenant, on_delete=models.PROTECT, related_name="billing")

    billing_entity = models.ForeignKey(TenantLegalEntity, on_delete=models.SET_NULL, null=True, blank=True, related_name="billing_for")
    # sheet 16: tenant.billing_entity. Which legal entity actually gets invoiced.

    po_required = models.BooleanField(default=False)
    po_format = models.CharField(max_length=100, blank=True)
    po_contact = models.CharField(max_length=255, blank=True)
    # sheet 16: tenant.purchase_order_requirements.

    payment_terms = models.CharField(max_length=100, blank=True)
    # sheet 16: tenant.payment_terms. E.g. "Net 30".

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenancy_tenant_billing"


# =====================================================================
# 11. Membership & RBAC
# =====================================================================

class TenantRoleAssignment(UUIDModel):
    """Which tenant role a user currently holds. FKs accounts.UserTbl
    directly — UserTbl.tenant already identifies which tenant a user
    belongs to (accounts.UserTbl is tenant-scoped: one row per tenant
    per person, login identity is tenant + email), so a separate
    tenant+user bridge table is unnecessary. This table's purpose is
    narrower than that: recording a specific, time-boxed role grant
    (TEMP_ACCESS_SET support via effective_from/to) with accountability
    for who granted it — detail accounts.UserTbl.role (a plain M2M)
    can't express on its own."""

    user = models.ForeignKey("accounts.UserTbl", on_delete=models.CASCADE, related_name="tenant_role_assignments")
    # The user this role applies to. Their tenant is user.tenant — not repeated here.

    role = models.ForeignKey("accounts.roles", on_delete=models.PROTECT, related_name="tenant_assignments")
    # The actual role table (sheet 18's 10 roles). NOT accounts.RoleCode — that's a TextChoices enum, not a table.

    granted_by = models.ForeignKey("accounts.UserTbl", on_delete=models.PROTECT, related_name="tenant_roles_granted")
    # Who granted this role.

    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    # Validity window — supports the TEMP_ACCESS_SET operation (temporary role grants that auto-expire).

    status = models.CharField(max_length=20, default="ACTIVE")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tenancy_tenant_role_assignment"


class TenantInvitation(TenantOwnedModel):
    """A pending invite sent to someone who isn't a member yet."""

    email = models.EmailField()
    role = models.ForeignKey("accounts.roles", on_delete=models.PROTECT, related_name="tenant_invitations")
    # What role they'll get once they accept.

    token = models.CharField(max_length=255, unique=True)
    # Unique invite link token.

    status = models.CharField(max_length=20, default="SENT")
    sent_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    # Invitations expire — no access before acceptance, per sheet 17's USER_INVITE rule.

    class Meta:
        db_table = "tenancy_tenant_invitation"


# =====================================================================
# 12. Workflow & Operational Logging
# =====================================================================

class TenantWorkflow(TenantOwnedModel, TimeStampedModel):
    """A generic, reusable approval-workflow instance — e.g. one row per
    tenant verification cycle, template approval, etc. Not required by
    sheet 16/19 directly, but gives every multi-step approval process in
    this file the same underlying engine instead of hand-coding each one."""

    workflow_type = models.CharField(max_length=50)
    # What kind of workflow this is (e.g. "TENANT_VERIFICATION", "TEMPLATE_APPROVAL").

    reference_table = models.CharField(max_length=50)
    reference_id = models.UUIDField()
    # Polymorphic pointer to whatever record this workflow is approving.

    status = models.CharField(max_length=20, default="IN_PROGRESS")

    class Meta:
        db_table = "tenancy_tenant_workflow"


class TenantWorkflowStep(UUIDModel):
    """One step in a TenantWorkflow — who needs to approve, in what order."""

    workflow = models.ForeignKey(TenantWorkflow, on_delete=models.CASCADE, related_name="steps")
    step_order = models.PositiveIntegerField()
    # The sequence this step happens in.

    assigned_role = models.ForeignKey("accounts.roles", on_delete=models.PROTECT, related_name="workflow_steps")
    # Which role is responsible for this step.

    decision = models.CharField(max_length=30, blank=True)
    comments = models.TextField(blank=True)
    # The outcome of this step, once actioned.

    actioned_by = models.ForeignKey("accounts.UserTbl", on_delete=models.SET_NULL, null=True, blank=True, related_name="workflow_steps_actioned")
    actioned_at = models.DateTimeField(null=True, blank=True)
    # Who actually did it and when.

    class Meta:
        db_table = "tenancy_tenant_workflow_step"
        ordering = ["workflow", "step_order"]


class TenantOperationLog(TenantOwnedModel):
    """NOT a substitute for governance.AuditEvent — that already covers
    per-record before/after audit trails. This is only for tracking
    async job runs (bulk import, retention sweep, etc)."""

    operation_type = models.CharField(max_length=100)
    # What kind of background job this is.

    performed_by = models.ForeignKey("accounts.UserTbl", on_delete=models.SET_NULL, null=True, blank=True, related_name="tenant_operations_performed")
    # Who triggered it, if a human did (vs. a scheduled job).

    status = models.CharField(max_length=20, default="STARTED")
    remarks = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tenancy_tenant_operation_log"


# =====================================================================
# 13. Configuration extras (things sheet 17's operations needed that
#     sheet 16/19 didn't explicitly list a table for)
# =====================================================================

class TenantTerminology(TenantOwnedModel):
    """Lets a tenant use their own words for platform concepts, e.g.
    calling a "Project" an "Assignment" in their own UI — required by
    the TERMINOLOGY_CONFIGURE operation."""

    canonical_code = models.CharField(max_length=100, help_text="System term, e.g. 'PROJECT'.")
    # The system's own internal name for the concept — never changes.

    display_label = models.CharField(max_length=100, help_text="Tenant's local term, e.g. 'Assignment'.")
    # What this tenant wants to call it instead, in their own UI.

    class Meta:
        db_table = "tenancy_tenant_terminology"
        constraints = [models.UniqueConstraint(fields=["tenant", "canonical_code"], name="uniq_tenant_terminology")]


class TenantNumberingConfig(TenantOwnedModel):
    """How this tenant's projects/reports get numbered — required by the
    DOCUMENT_NUMBERING_CONFIGURE operation."""

    document_type = models.CharField(max_length=30)
    # Which kind of document this numbering pattern applies to.

    pattern = models.CharField(max_length=100, help_text="e.g. 'PRJ-{YYYY}-{SEQ}'.")
    # The actual numbering template.

    current_sequence = models.PositiveIntegerField(default=0)
    # The next number to use — increments each time a new document of this type is created.

    class Meta:
        db_table = "tenancy_tenant_numbering_config"
        constraints = [models.UniqueConstraint(fields=["tenant", "document_type"], name="uniq_tenant_numbering")]


class TenantApprovalMatrix(TenantOwnedModel, TimeStampedModel):
    """Which roles must sign off before a project/report is approved —
    required by the APPROVAL_MATRIX_CONFIGURE operation."""

    project = models.ForeignKey("Project", on_delete=models.CASCADE, null=True, blank=True, related_name="approval_matrix_overrides")
    # Null = this is the tenant-wide default. Set = this project overrides the default for itself.

    document_type = models.CharField(max_length=20, choices=[("PROJECT", "Project"), ("REPORT", "Report")])

    sequence = models.JSONField(default=list, help_text="Ordered list of accounts.roles codes required to approve.")
    # The actual approval chain, in order.

    class Meta:
        db_table = "tenancy_tenant_approval_matrix"


class TenantNotificationSettings(TenantOwnedModel, TimeStampedModel):
    """Who gets notified about what — required by the
    NOTIFICATION_CONFIGURE operation."""

    event_type = models.CharField(max_length=100)
    # Which system event this rule applies to.

    channels = models.JSONField(default=list, blank=True)
    # How the notification is delivered (email, SMS, in-app, etc.).

    escalation_rules = models.JSONField(default=dict, blank=True)
    # What happens if the notification isn't acted on in time.

    class Meta:
        db_table = "tenancy_tenant_notification_settings"


class ConflictOfInterestDeclaration(TenantOwnedModel, TimeStampedModel):
    """A declared (or reviewed) conflict of interest — required by the
    COI_REVIEW operation."""

    project = models.ForeignKey("Project", on_delete=models.SET_NULL, null=True, blank=True, related_name="coi_declarations")
    # Which project this conflict relates to, if project-specific.

    declared_by = models.ForeignKey("accounts.UserTbl", on_delete=models.PROTECT, related_name="coi_declarations")
    # Who's declaring the conflict.

    has_conflict = models.BooleanField()
    details = models.TextField(blank=True)
    mitigation = models.TextField(blank=True)
    # Whether there is one, what it is, and how it's being managed.

    status = models.CharField(max_length=20, default="SUBMITTED")

    reviewed_by = models.ForeignKey("accounts.UserTbl", on_delete=models.SET_NULL, null=True, blank=True, related_name="coi_reviews_done")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    # Who reviewed it and when.

    class Meta:
        db_table = "tenancy_conflict_of_interest_declaration"


class DataExportRequest(TenantOwnedModel, TimeStampedModel):
    """A formal, approved request to export the tenant's data — required
    by the DATA_EXPORT_REQUEST operation. Mirrors DisclosureRequest's
    shape since both need purpose, scope, and an approval trail."""

    requested_by = models.ForeignKey("accounts.UserTbl", on_delete=models.PROTECT, related_name="export_requests_made")
    purpose = models.TextField()
    scope = models.JSONField(default=dict)
    # What's being exported and why.

    status = models.CharField(max_length=20, default="REQUESTED")

    approved_by = models.ForeignKey("accounts.UserTbl", on_delete=models.SET_NULL, null=True, blank=True, related_name="export_requests_approved")
    approved_at = models.DateTimeField(null=True, blank=True)
    # Who approved the export and when.

    expiry_date = models.DateTimeField(null=True, blank=True)
    # The exported package itself expires — it isn't a permanent open door.

    watermark_applied = models.BooleanField(default=False)
    # Whether the export was watermarked, per sheet 17's security rule for this operation.

    class Meta:
        db_table = "tenancy_data_export_request"


# =====================================================================
# 14. Projects — the tenant's own work requisition (a job opening,
#     before any candidate is attached). NOT the same as
#     experience.ProjectRecord (a candidate's own resume entry of past
#     work already performed).
# =====================================================================

class Project(TenantOwnedModel, TimeStampedModel, UUIDModel):
    """A specific piece of work the tenant is running."""

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

    business_unit = models.ForeignKey(
        Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name="projects",
        help_text="Must be an Organization row with organization_type in BRANCH/DEPARTMENT/OPERATING_UNIT — enforce in clean().",
    )  # Which internal division owns this project, if any.

    location = models.ForeignKey(TenantLocation, on_delete=models.SET_NULL, null=True, blank=True, related_name="projects")
    # Which of the tenant's locations this project is based out of, if any.

    project_code = models.CharField(max_length=50)
    project_name = models.CharField(max_length=250)
    project_type = models.CharField(max_length=100, blank=True)
    # Basic project identity.

    client_organization = models.ForeignKey(Organization, on_delete=models.PROTECT, null=True, blank=True, related_name="client_projects")
    # Which external client this project is for, if any.

    industry = models.ForeignKey("catalog.ReferenceValue", on_delete=models.PROTECT, null=True, blank=True, related_name="projects")
    scope_catalog_entries = models.ManyToManyField("catalog.ScopeCatalog", blank=True, related_name="projects")
    # What industry/scopes this project covers.

    country_code = models.CharField(max_length=2, validators=[validate_iso_country_code])
    city = models.CharField(max_length=120, blank=True)
    # Where the work happens.

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    # Project timeline.

    confidentiality_classification = models.CharField(max_length=20, choices=Confidentiality.choices, default=Confidentiality.INTERNAL)
    # How sensitive this project's details are — drives masking/disclosure rules.

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "tenancy_project"
        constraints = [models.UniqueConstraint(fields=["tenant", "project_code"], name="uniq_project_code_per_tenant")]

    def clean(self):
        super().clean()
        if self.business_unit_id and self.business_unit.organization_type not in Organization.INTERNAL_STRUCTURE_TYPES:
            raise ValidationError({"business_unit": "Must reference a BRANCH/DEPARTMENT/OPERATING_UNIT Organization row."})

    def __str__(self):
        return self.project_name


class ProjectMembership(models.Model):
    """Internal tenant staff assigned to manage a project — distinct from
    ProjectPlacement below, which is the external candidate's placement."""

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey("accounts.UserTbl", on_delete=models.CASCADE, related_name="project_memberships")
    # Which tenant staff member, on which project.

    role = models.ForeignKey("accounts.roles", on_delete=models.PROTECT, related_name="project_memberships")
    # Their role specifically on this project (can differ from their general tenant role).

    scopes = models.JSONField(default=list, blank=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    entitlement = models.JSONField(default=dict, blank=True)
    # What they're specifically allowed to do/see on this project, and for how long.

    assigned_by = models.ForeignKey("accounts.UserTbl", on_delete=models.PROTECT, related_name="project_memberships_assigned")

    class Meta:
        db_table = "tenancy_project_membership"
        constraints = [models.UniqueConstraint(fields=["project", "user"], name="uniq_project_membership")]


class ProjectRequirement(UUIDModel):
    """What kind of professional this project needs — role, scope,
    experience level."""

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="requirements")

    role_code = models.ForeignKey(
        "catalog.ReferenceValue", on_delete=models.PROTECT, related_name="project_requirements",
        help_text="option_set.option_type=PROFESSIONAL_ROLE, matching professionals.ProfessionalProfile.primary_role.",
    )  # What role is needed (from the same lookup table professional profiles use for their own primary role).

    required_count = models.PositiveIntegerField()
    # How many people with this profile are needed.

    minimum_experience_years = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Minimum years of experience required.

    is_mandatory = models.BooleanField(default=True)
    # Whether this requirement is a hard must-have vs. a nice-to-have.

    remarks = models.TextField(blank=True)

    class Meta:
        db_table = "tenancy_project_requirement"


class ProjectRequirementScope(models.Model):
    """Which specific scopes this requirement covers — one requirement
    can span several scopes."""

    requirement = models.ForeignKey(ProjectRequirement, on_delete=models.CASCADE, related_name="scopes")
    scope_catalog = models.ForeignKey("catalog.ScopeCatalog", on_delete=models.PROTECT, related_name="requirement_links")

    class Meta:
        db_table = "tenancy_project_requirement_scope"
        constraints = [models.UniqueConstraint(fields=["requirement", "scope_catalog"], name="uniq_requirement_scope")]


class ProjectCandidate(UUIDModel):
    """The shortlist stage — masked, before any identity/details are
    disclosed to the tenant."""

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="candidates")
    professional = models.ForeignKey("professionals.ProfessionalProfile", on_delete=models.PROTECT, related_name="project_shortlists")
    # Which candidate has been shortlisted for this project.

    shortlist_status = models.CharField(max_length=30, default="SHORTLISTED")
    shortlisted_by = models.ForeignKey("accounts.UserTbl", on_delete=models.PROTECT, related_name="shortlists_made")
    # Who added them to the shortlist.

    class Meta:
        db_table = "tenancy_project_candidate"
        constraints = [models.UniqueConstraint(fields=["project", "professional"], name="uniq_project_candidate")]


class DisclosureRequest(TenantOwnedModel, TimeStampedModel, UUIDModel):
    """A formal, field-level request to see part of a candidate's
    profile — never a blanket request, always specific and purpose-bound."""

    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        APPROVED = "APPROVED", "Approved"
        DECLINED = "DECLINED", "Declined"
        EXPIRED = "EXPIRED", "Expired"

    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name="disclosure_requests")
    professional = models.ForeignKey("professionals.ProfessionalProfile", on_delete=models.PROTECT, related_name="disclosure_requests")
    # PROTECT (not CASCADE) on both — deleting a project must never erase the record of what a
    # candidate consented to.

    requested_by = models.ForeignKey("accounts.UserTbl", on_delete=models.PROTECT, related_name="disclosure_requests_made")
    # Who's asking — normally a Project Manager.

    requested_fields = models.JSONField(default=list, help_text="Which profile fields are being requested.")
    # Exactly which fields, not a blanket "everything."

    purpose = models.TextField()
    # Why they're asking — required, per sheet 17's "field-level and purpose-bound" rule.

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
    expires_at = models.DateTimeField(null=True, blank=True)
    # The request itself has an expiry — access isn't open-ended.

    class Meta:
        db_table = "tenancy_disclosure_request"


class CandidateConsent(UUIDModel):
    """The candidate's own decision on a disclosure request. Only the
    candidate can ever fill this in — nobody consents on their behalf."""

    class Decision(models.TextChoices):
        GRANTED = "GRANTED", "Granted"
        DECLINED = "DECLINED", "Declined"
        WITHDRAWN = "WITHDRAWN", "Withdrawn"

    disclosure_request = models.ForeignKey(DisclosureRequest, on_delete=models.PROTECT, related_name="consents")
    professional = models.ForeignKey("professionals.ProfessionalProfile", on_delete=models.PROTECT, related_name="consents_given")
    # PROTECT on both, same reasoning as DisclosureRequest — never lose the record of a consent decision.

    decision = models.CharField(max_length=15, choices=Decision.choices)

    fields = models.JSONField(default=list, help_text="Subset of requested_fields actually consented to.")
    # The candidate might not agree to ALL requested fields — this can be a subset.

    decided_at = models.DateTimeField(auto_now_add=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    # Consent can be withdrawn later — this records when, if it happens.

    class Meta:
        db_table = "tenancy_candidate_consent"


class ProjectPlacement(UUIDModel):
    """The tenant-side placement record, once a candidate is confirmed
    onto a project. Links to the candidate's own
    experience.ProfessionalAssignment rather than re-describing the same
    placement twice in two different shapes."""

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="placements")
    professional = models.ForeignKey("professionals.ProfessionalProfile", on_delete=models.PROTECT, related_name="project_placements")
    # Who's been placed, on which project.

    professional_assignment = models.ForeignKey(
        "experience.ProfessionalAssignment", on_delete=models.SET_NULL, null=True, blank=True, related_name="tenant_placement",
        help_text="Link to the candidate's own experience.ProfessionalAssignment row (assignment_type=PROJECT) once confirmed.",
    )  # Once confirmed, this links out to the matching row on the candidate's own resume-history side.

    assigned_role = models.CharField(max_length=120)
    deployment_start = models.DateField()
    deployment_end = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default="ACTIVE")

    class Meta:
        db_table = "tenancy_project_placement"


class ProjectScopeLink(UUIDModel, TimeStampedModel):
    """The per-scope technical-experience claim on the tenant side —
    authority exercised, allocation %, verified field days. Mirrors
    experience.ProjectScope in shape but is tenant-owned; links to it
    once the candidate's matching resume entry exists."""

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="scope_links")
    placement = models.ForeignKey(ProjectPlacement, on_delete=models.SET_NULL, null=True, blank=True, related_name="scope_links")
    professional = models.ForeignKey("professionals.ProfessionalProfile", on_delete=models.PROTECT, related_name="project_scope_links")
    # Which project, which placement, which candidate this claim belongs to.

    experience_project_scope = models.ForeignKey(
        "experience.ProjectScope", on_delete=models.SET_NULL, null=True, blank=True, related_name="tenant_scope_link",
        help_text="Link to the matching candidate-side experience.ProjectScope row, once created.",
    )  # Link to the matching row on the candidate's own experience/resume side, once created.

    industry = models.ForeignKey("catalog.ReferenceValue", on_delete=models.PROTECT, related_name="project_scope_links")
    scope_catalog = models.ForeignKey("catalog.ScopeCatalog", on_delete=models.PROTECT, related_name="project_scope_links")
    # Which industry and scope this specific claim covers.

    authority_action_code = models.ForeignKey(
        "catalog.ReferenceValue", on_delete=models.PROTECT, related_name="project_scope_link_authority",
        help_text="option_set.option_type must be AUTHORITY_ACTION, matching experience.ProjectScope.authority_action.",
    )  # What level of authority they exercised (e.g. observed vs. independently signed off).

    allocation_percent = models.PositiveSmallIntegerField()
    # What percentage of their time was allocated to this scope.

    verified_field_days = models.PositiveIntegerField(null=True, blank=True)
    # How many verified field days this represents.

    evidence_document = models.ForeignKey(TenantDocument, on_delete=models.SET_NULL, null=True, blank=True, related_name="scope_link_evidence")
    # Supporting proof for this specific claim, if any.

    class Meta:
        db_table = "tenancy_project_scope_link"
        constraints = [models.UniqueConstraint(fields=["project", "professional", "scope_catalog"], name="uniq_project_scope_link")]
