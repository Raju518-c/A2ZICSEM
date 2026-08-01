"""accounts: tenant-scoped authentication, permanent tenant URL
registration, registration approval and consent history.

Ownership and access: Platform Super Admin manages platform access.
Tenant Admin approves registrations belonging to their tenant.

The project keeps email unique only within a tenant, so authentication uses
a custom backend that resolves users by tenant portal slug + email rather
than Django's default global username semantics.
"""

import secrets

from django.conf import settings
from django.contrib.auth.hashers import (
    check_password as django_check_password,
    identify_hasher,
    make_password,
)
from django.core.exceptions import ValidationError
import secrets

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Lower

from core.models import CreatedOnlyModel, TimeStampedModel, UUIDModel
from core.validators import validate_calling_code, validate_iso_country_code

validate_mobile_number = RegexValidator(
    regex=r"^\d{10,15}$",
    message="Enter digits only, 10-15 digits.",
    code="invalid_mobile_number",
)


class RoleCode(models.TextChoices):
    TENANT_ADMIN = "TENANT_ADMIN", "Tenant admin"
    PROFESSIONAL = "PROFESSIONAL", "Professional"
    REVIEWER = "REVIEWER", "Reviewer"


def default_role_codes():
    return [RoleCode.PROFESSIONAL]


def validate_role_codes(value):
    if not isinstance(value, list):
        raise ValidationError("role_codes must be a list.", code="invalid_role_codes")
    allowed = set(RoleCode.values)
    invalid = sorted(set(value) - allowed)
    if invalid:
        raise ValidationError(
            "Invalid role code(s): %(invalid)s.",
            code="invalid_role_codes",
            params={"invalid": ", ".join(invalid)},
        )
    
class roles(models.Model):
    """Role code and name mapping."""

    Roles_for_choices = [
        ('super admin', 'super admin'),
        ('tenant admin', 'tenant admin')    
    ]
    code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=32, help_text="Role name.")
    roles_for = models.CharField(max_length=16, choices=Roles_for_choices, default='super admin')
    tenant = models.ForeignKey(
        "tenancy.Tenant",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="roles",
        db_index=True,
        help_text="Tenant registration and login context. Required for all "
        "non-platform users; NULL only for Platform Super Admin.",
    )

    created = models.DateTimeField(auto_now_add=True, help_text="Date and time of creation.")


class UserTbl(UUIDModel):
    """Custom tenant-scoped account record. A person may register
    separately in several tenants using the same email, creating one
    tenant-scoped User per tenant.

    Key rules: Login identity is Tenant + Email. Email and mobile are
    unique only within a tenant. Platform Super Admin has tenant=NULL.
    Candidate/Mentor is not stored as an account role.
    """

    class ApprovalStatus(models.TextChoices):
        PENDING_APPROVAL = "PENDING_APPROVAL", "Pending approval"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        SUSPENDED = "SUSPENDED", "Suspended"

    class MfaMethod(models.TextChoices):
        NONE = "NONE", "None"
        AUTHENTICATOR = "AUTHENTICATOR", "Authenticator app"
        SMS = "SMS", "SMS"
        EMAIL = "EMAIL", "Email"

    tenant = models.ForeignKey(
        "tenancy.Tenant",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="users",
        db_index=True,
        help_text="Tenant registration and login context. Required for all "
        "non-platform users; NULL only for Platform Super Admin.",
    )
    email = models.EmailField(
        max_length=254, help_text="Primary login and communication email."
    )
    mobile_country_code = models.CharField(
        max_length=5,
        validators=[validate_calling_code],
        help_text="Country calling code stored separately.",
    )
    mobile_number = models.CharField(
        max_length=15,
        validators=[validate_mobile_number],
        help_text="Mobile number for verification and recovery.",
    )
    password = models.CharField(
        max_length=128,
        help_text="Authentication secret. Minimum policy 12 characters; "
        "hashed by the authentication layer; never stored or returned as "
        "plain text.",
    )
    # role_codes = models.JSONField(
    #     default=default_role_codes,
    #     blank=True,
    #     validators=[validate_role_codes],
    #     help_text="Tenant application roles; Candidate/Mentor classification "
    #     "is separate. Platform Super Admin uses is_superuser.",
    # )    
    role = models.ManyToManyField(roles, blank=True)
    is_candidate = models.BooleanField(
        default=False, help_text="True only for candidates."
    )
    is_mentor = models.BooleanField(
        default=False, help_text="True only for mentors."
    )
    
    approval_status = models.CharField(
        max_length=30,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING_APPROVAL,
        db_index=True,
        help_text="Tenant Admin approval state.",
    )
    email_verified_at = models.DateTimeField(
        null=True, blank=True, help_text="Email verification timestamp."
    )
    mobile_verified_at = models.DateTimeField(
        null=True, blank=True, help_text="Mobile verification timestamp."
    )
    mfa_method = models.CharField(
        max_length=20,
        choices=MfaMethod.choices,
        default=MfaMethod.EMAIL,
        help_text="Selected two-factor authentication method.",
    )
    approved_by = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="users_approved",
        help_text="Approver of the user account. Same-tenant Tenant Admin "
        "or Platform Super Admin; cannot approve self.",
    )
    approved_at = models.DateTimeField(
        null=True, blank=True, help_text="Approval timestamp."
    )
    rejection_reason = models.TextField(
        max_length=2000, blank=True, help_text="Reason for rejection or return."
    )
    is_active = models.BooleanField(
        default=False,
        help_text="Django authentication active flag. Set true only after "
        "approval and required verification; may be false for suspension.",
    )
    is_staff = models.BooleanField(
        default=False, help_text="Django Admin access flag."
    )
    is_superuser = models.BooleanField(
        default=False,
        help_text="True only for Platform Super Admin; tenant must be NULL. "
        "Platform-wide superuser flag.",
    )
    failed_login_attempts = models.PositiveSmallIntegerField(
        default=0, help_text="Failed authentication counter."
    )
    locked_until = models.DateTimeField(
        null=True, blank=True, help_text="Temporary lock expiry."
    )
    last_login = models.DateTimeField(
        null=True, blank=True, help_text="Last successful login."
    )
    date_joined = models.DateTimeField(
        auto_now_add=True, help_text="User creation timestamp."
    )
    updated_at = models.DateTimeField(auto_now=True)

    # Django still requires a unique USERNAME_FIELD on AUTH_USER_MODEL.
    # Login itself uses tenant portal slug + email through the custom backend.
    USERNAME_FIELD = "public_id"
    REQUIRED_FIELDS = ["email", "mobile_country_code", "mobile_number"]

    class Meta:
        db_table = "accounts_user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["email"]
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                "tenant",
                name="uniq_user_tenant_lower_email",
            ),
            models.UniqueConstraint(
                fields=["tenant", "mobile_country_code", "mobile_number"],
                name="uniq_user_tenant_mobile",
            ),
            models.CheckConstraint(
                check=~Q(approved_by=F("id")),
                name="chk_user_approved_by_not_self",
            ),
            models.CheckConstraint(
                check=(
                    ~Q(approval_status="APPROVED") | Q(approved_at__isnull=False)
                ),
                name="chk_user_approved_at_required_when_approved",
            ),
            models.CheckConstraint(
                check=(
                    ~Q(approval_status="REJECTED") | ~Q(rejection_reason="")
                ),
                name="chk_user_rejection_reason_required_when_rejected",
            ),
        ]

    # Plain properties (not inherited from AbstractBaseUser) required by
    # Django's check_user_model / auth machinery whenever AUTH_USER_MODEL
    # points at a model — must not be methods (see auth.C009/C010).
    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()

        if self.password:
            try:
                identify_hasher(self.password)
            except Exception:
                self.password = make_password(self.password)

        super().save(*args, **kwargs)


    def check_password(self, password):
        stored_password = self.password or ""

        # Normal Django hashed password check
        if django_check_password(password, stored_password):
            return True

        # Legacy plain-text password support
        if stored_password and secrets.compare_digest(stored_password, password):
            self.password = make_password(password)
            self.save(update_fields=["password", "updated_at"])
            return True

        return False

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser or self.is_staff

    def __str__(self):
        return self.email   
    

class RegistrationApplication(TimeStampedModel, UUIDModel):
    """Stores each user registration submission and Tenant Admin approval
    decision. The permanent tenant URL determines tenant automatically.

    Key rules: No expiring user invitation token is used. Only one pending
    application version is allowed per tenant user. Approval is limited to
    the same tenant.
    """

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        RETURNED = "RETURNED", "Returned"
        CANCELLED = "CANCELLED", "Cancelled"

    tenant = models.ForeignKey(
        "tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="registration_applications",
        db_index=True,
        help_text="Tenant receiving the registration. Derived from the "
        "permanent tenant URL; cannot be changed by request payload.",
    )
    user = models.ForeignKey(
        UserTbl,
        on_delete=models.CASCADE,
        related_name="registration_applications",
        db_index=True,
        help_text="Tenant-scoped user submitting the application. "
        "User.tenant must equal tenant.",
    )
    application_version = models.PositiveIntegerField(
        default=1, help_text="Submission version; incremented for resubmission."
    )
    selected_industry = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        related_name="registration_applications",
        help_text="Industry selected during Stage 1. Must be active INDUSTRY "
        "and assigned to tenant through TenantOperation.",
    )
    selected_scope = models.ForeignKey(
        "catalog.ScopeCatalog",
        on_delete=models.PROTECT,
        related_name="registration_applications",
        help_text="Primary inspection/survey scope. Scope.industry must "
        "equal selected_industry.",
    )
    selected_operating_country = models.CharField(
        max_length=2,
        validators=[validate_iso_country_code],
        help_text="Country of the tenant operation selected by user. Must "
        "match an active TenantOperation for selected industry.",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        help_text="Application workflow status.",
    )
    stage1_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot of Stage 1 data reviewed by Tenant Admin. "
        "Immutable after submission; excludes password and OTP.",
    )
    submitted_at = models.DateTimeField(
        null=True, blank=True, help_text="Submission timestamp."
    )
    reviewed_by = models.ForeignKey(
        UserTbl,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="registration_applications_reviewed",
        help_text="User who reviewed the application. Must be same-tenant "
        "Tenant Admin or Platform Super Admin.",
    )
    reviewed_at = models.DateTimeField(
        null=True, blank=True, help_text="Review decision timestamp."
    )
    decision_reason = models.TextField(
        max_length=2000, blank=True, help_text="Review explanation."
    )

    class Meta:
        db_table = "accounts_registration_application"
        verbose_name = "Registration Application"
        verbose_name_plural = "Registration Applications"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "user", "application_version"],
                name="uniq_registration_application_tenant_user_version",
            ),
            models.CheckConstraint(
                check=(Q(status="DRAFT") | Q(submitted_at__isnull=False)),
                name="chk_registration_application_submitted_at_required",
            ),
            models.CheckConstraint(
                check=(
                    ~Q(status__in=["APPROVED", "REJECTED", "RETURNED"])
                    | Q(reviewed_at__isnull=False)
                ),
                name="chk_registration_application_reviewed_at_required",
            ),
            models.CheckConstraint(
                check=(
                    ~Q(status__in=["REJECTED", "RETURNED"])
                    | ~Q(decision_reason="")
                ),
                name="chk_registration_application_decision_reason_required",
            ),
        ]

    def __str__(self):
        return f"{self.user} v{self.application_version} ({self.status})"


class ConsentRecord(CreatedOnlyModel):
    """Append-only record of legal consents and professional declarations,
    including version and timestamp.

    Key rules: Consent history is never overwritten or hard-deleted.
    Marketing consent is optional and defaults to false. Resume-processing
    consent is required only when a resume is uploaded.
    """

    class ConsentType(models.TextChoices):
        TERMS = "TERMS", "Terms"
        PRIVACY = "PRIVACY", "Privacy"
        RESUME_PROCESSING = "RESUME_PROCESSING", "Resume processing"
        MARKETING = "MARKETING", "Marketing"
        CLIENT_RESUME_SHARING = "CLIENT_RESUME_SHARING", "Client resume sharing"
        REFERENCE_SHARING = "REFERENCE_SHARING", "Reference sharing"
        PROFILE_ACCURACY = "PROFILE_ACCURACY", "Profile accuracy"
        CONFLICT_OF_INTEREST = "CONFLICT_OF_INTEREST", "Conflict of interest"

    class Source(models.TextChoices):
        WEB = "WEB", "Web"
        MOBILE = "MOBILE", "Mobile"
        ADMIN = "ADMIN", "Admin"
        IMPORT = "IMPORT", "Import"

    tenant = models.ForeignKey(
        "tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="consent_records",
        db_index=True,
        help_text="Same tenant as user and professional.",
    )
    user = models.ForeignKey(
        UserTbl,
        on_delete=models.CASCADE,
        related_name="consent_records",
        db_index=True,
        help_text="User giving or withdrawing consent. User.tenant must "
        "equal tenant.",
    )
    professional = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="consent_records",
        help_text="Optional professional context. Required for "
        "profile/resume declarations when profile exists.",
    )
    consent_type = models.CharField(
        max_length=40,
        choices=ConsentType.choices,
        help_text="Type of consent or declaration.",
    )
    document_version = models.CharField(
        max_length=30, help_text="Version of the accepted document or wording."
    )
    jurisdiction = models.CharField(
        max_length=20, blank=True, help_text="Applicable legal jurisdiction."
    )
    is_granted = models.BooleanField(help_text="Whether consent was granted.")
    granted_at = models.DateTimeField(
        null=True, blank=True, help_text="Grant timestamp."
    )
    withdrawn_at = models.DateTimeField(
        null=True, blank=True, help_text="Withdrawal timestamp."
    )
    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.WEB,
        help_text="Channel through which consent was recorded.",
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, help_text="Network address recorded for audit."
    )
    user_agent = models.TextField(
        max_length=1000, blank=True, help_text="Client application/browser information."
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="May hold client/template context or conflict details; no secrets.",
    )

    class Meta:
        db_table = "accounts_consent_record"
        verbose_name = "Consent Record"
        verbose_name_plural = "Consent Records"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=(Q(is_granted=False) | Q(granted_at__isnull=False)),
                name="chk_consent_record_granted_at_required",
            ),
            models.CheckConstraint(
                check=(
                    Q(withdrawn_at__isnull=True)
                    | Q(granted_at__isnull=True)
                    | Q(withdrawn_at__gt=F("granted_at"))
                ),
                name="chk_consent_record_withdrawn_after_granted",
            ),
        ]

    def __str__(self):
        return f"{self.user} — {self.consent_type}"
