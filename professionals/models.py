"""professionals: Stage 1 and Stage 2 professional passport, system/admin
classification, credentials, capabilities and contacts.

Ownership and access: Professional enters data. Tenant Admin/Reviewer
verifies. Candidate or Mentor classification is confirmed through
ProfessionalReview.

Fields marked in the architecture as "Stage 1" / "Stage 2" / "Conditional"
are enforced as required by stage-specific services at submission time, not
as DB-level NOT NULL — the document is explicit that "draft records may be
incomplete." blank=True here reflects that, while max_length/choices/format
validators still match the document exactly.
"""

from django.conf import settings
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q

from core.choices import DataClassification, ResumeVisibility, VerificationStatus
from core.fields import EncryptedCharField, EncryptedTextField
from core.models import (
    ArchivableModel,
    CreatedOnlyModel,
    TenantOwnedModel,
    TimeStampedModel,
    UUIDModel,
)
from core.validators import (
    validate_e164_phone,
    validate_iana_timezone,
    validate_iso_country_code,
    validate_not_future_date,
    validate_past_date,
)


class ProfessionalProfile(UUIDModel, TenantOwnedModel, TimeStampedModel):
    """One tenant-specific professional passport per User. Contains Stage 1
    identity/routing fields and Stage 2 common profile, availability,
    commercial and deployment fields.

    Key rules: Unique tenant+user. Draft records may be incomplete;
    Stage-specific services enforce required fields on submission.
    Candidate/Mentor classification cannot be edited directly.
    """

    class ProfileStatus(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        STAGE1_COMPLETE = "STAGE1_COMPLETE", "Stage 1 complete"
        STAGE2_INCOMPLETE = "STAGE2_INCOMPLETE", "Stage 2 incomplete"
        SUBMITTED = "SUBMITTED", "Submitted"
        APPROVED = "APPROVED", "Approved"
        RETURNED = "RETURNED", "Returned"
        REJECTED = "REJECTED", "Rejected"
        ARCHIVED = "ARCHIVED", "Archived"

    class Classification(models.TextChoices):
        UNCLASSIFIED = "UNCLASSIFIED", "Unclassified"
        CANDIDATE = "CANDIDATE", "Candidate"
        MENTOR = "MENTOR", "Mentor"

    class ClassificationStatus(models.TextChoices):
        NOT_ASSESSED = "NOT_ASSESSED", "Not assessed"
        SYSTEM_SUGGESTED = "SYSTEM_SUGGESTED", "System suggested"
        UNDER_REVIEW = "UNDER_REVIEW", "Under review"
        CONFIRMED = "CONFIRMED", "Confirmed"

    class NameDisplayOrder(models.TextChoices):
        GIVEN_FAMILY = "GIVEN_FAMILY", "Given family"
        FAMILY_GIVEN = "FAMILY_GIVEN", "Family given"
        SINGLE_NAME = "SINGLE_NAME", "Single name"

    class ExperienceBand(models.TextChoices):
        NONE = "NONE", "None"
        LT_1 = "LT_1", "Less than 1 year"
        ONE_TO_3 = "1_TO_3", "1 to 3 years"
        THREE_TO_6 = "3_TO_6", "3 to 6 years"
        SIX_TO_12 = "6_TO_12", "6 to 12 years"
        TWELVE_PLUS = "12_PLUS", "12+ years"

    class SummarySource(models.TextChoices):
        USER = "USER", "User"
        SYSTEM_GENERATED = "SYSTEM_GENERATED", "System generated"
        MIXED = "MIXED", "Mixed"

    user = models.OneToOneField(
        "accounts.UserTbl",
        on_delete=models.CASCADE,
        related_name="professional_profile",
        help_text="Authentication account for the professional. Unique "
        "with tenant; user role must include PROFESSIONAL.",
    )
    registration_application = models.OneToOneField(
        "accounts.RegistrationApplication",
        on_delete=models.PROTECT,
        related_name="professional_profile",
        help_text="Registration application that created the profile. Must "
        "refer to the same tenant and user.",
    )
    profile_status = models.CharField(
        max_length=30,
        choices=ProfileStatus.choices,
        default=ProfileStatus.DRAFT,
        db_index=True,
        help_text="Current profile workflow status.",
    )
    current_classification = models.CharField(
        max_length=20,
        choices=Classification.choices,
        default=Classification.UNCLASSIFIED,
        help_text="Current professional classification.",
    )
    classification_status = models.CharField(
        max_length=30,
        choices=ClassificationStatus.choices,
        default=ClassificationStatus.NOT_ASSESSED,
        help_text="Status of classification decision.",
    )
    classified_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="professionals_classified",
        help_text="User who confirmed classification. Tenant Admin, "
        "Reviewer or Platform Super Admin; cannot be profile owner.",
    )
    classified_at = models.DateTimeField(
        null=True, blank=True, help_text="Classification timestamp."
    )
    classification_ruleset_version = models.CharField(
        max_length=30, blank=True, help_text="Version of rules used for classification."
    )
    profile_version = models.PositiveIntegerField(
        default=1, help_text="Version used for reviews and resume snapshots."
    )
    completion_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Cached profile completion percentage.",
    )
    legal_full_name = models.CharField(
        max_length=160, blank=True, help_text="Name matching identity documents."
    )
    display_name = models.CharField(
        max_length=160, blank=True, help_text="Name displayed on profile and resume."
    )
    first_name = models.CharField(max_length=80, blank=True, help_text="Given/first name.")
    middle_name = models.CharField(
        max_length=80, blank=True, help_text="Middle name where applicable."
    )
    last_name = models.CharField(
        max_length=80, blank=True, help_text="Family/last name; may be blank only "
        "for single-name users."
    )
    preferred_name = models.CharField(
        max_length=80, blank=True, help_text="Preferred professional name."
    )
    name_display_order = models.CharField(
        max_length=20,
        choices=NameDisplayOrder.choices,
        blank=True,
        help_text="International name rendering order.",
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        validators=[validate_past_date],
        help_text="Date of birth; not resume-visible by default.",
    )
    gender = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="professional_profiles_gender",
        help_text="Optional gender value. option_set must be GENDER.",
    )
    nationalities = models.JSONField(
        default=list, blank=True, help_text="One or more nationalities/citizenships."
    )
    country_of_residence = models.CharField(
        max_length=2,
        blank=True,
        validators=[validate_iso_country_code],
        help_text="Country of residence.",
    )
    city = models.CharField(max_length=120, blank=True, help_text="City of residence.")
    timezone = models.CharField(
        max_length=64,
        blank=True,
        validators=[validate_iana_timezone],
        help_text="Communication timezone.",
    )
    address_line_1 = EncryptedCharField(
        max_length=200, blank=True, help_text="Residential address line 1. Restricted PII."
    )
    address_line_2 = EncryptedCharField(
        max_length=200, blank=True, help_text="Residential address line 2. Restricted PII."
    )
    postal_code = EncryptedCharField(
        max_length=20, blank=True, help_text="Residential postal code. Restricted PII."
    )
    address_country_code = models.CharField(
        max_length=2,
        blank=True,
        validators=[validate_iso_country_code],
        help_text="Country of residential address. Required when any address "
        "field is supplied.",
    )
    personal_email = models.EmailField(
        max_length=254,
        blank=True,
        help_text="Professional contact email for authorised resume use.",
    )
    primary_phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[validate_e164_phone],
        help_text="Professional contact phone.",
    )
    linkedin_url = models.URLField(
        max_length=500, blank=True, help_text="LinkedIn profile link."
    )
    existing_resume = models.ForeignKey(
        "evidence.EvidenceDocument",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="professional_profiles_resume",
        help_text="Optional professional resume. Evidence type must be "
        "RESUME and same professional.",
    )
    profile_photo_evidence = models.ForeignKey(
        "evidence.EvidenceDocument",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="professional_profiles_photo",
        help_text="Optional professional photograph. Evidence type must be "
        "PHOTOGRAPH and same professional.",
    )
    photo_resume_visibility = models.CharField(
        max_length=30,
        choices=ResumeVisibility.choices,
        default=ResumeVisibility.CLIENT_SPECIFIC,
        help_text="Controls photo use in client resumes. Required when photo exists.",
    )
    primary_industry = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="professional_profiles_primary_industry",
        help_text="Primary industry selected during registration. Must be "
        "active INDUSTRY permitted by TenantOperation.",
    )
    primary_scope = models.ForeignKey(
        "catalog.ScopeCatalog",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="professional_profiles_primary_scope",
        help_text="Primary inspection/survey scope. Scope.industry must "
        "equal primary_industry.",
    )
    self_declared_career_stage = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="professional_profiles_career_stage",
        help_text="Self-declared career stage used only for initial routing. "
        "option_set must be CAREER_STAGE.",
    )
    current_job_title = models.CharField(
        max_length=120, blank=True, help_text="Current or most recent professional title."
    )
    initial_experience_band = models.CharField(
        max_length=20,
        choices=ExperienceBand.choices,
        blank=True,
        help_text="Approximate experience used only for initial routing.",
    )
    highest_qualification_level = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="professional_profiles_qualification_level",
        help_text="Highest qualification selected at Stage 1. option_set "
        "must be QUALIFICATION_LEVEL.",
    )
    headline = models.CharField(
        max_length=140, blank=True, help_text="Professional headline."
    )
    summary = models.TextField(
        max_length=2000, blank=True, help_text="Client-ready professional summary."
    )
    key_strengths = models.JSONField(
        default=list, blank=True, help_text="Key professional strengths (max 12 tags)."
    )
    primary_role = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="professional_profiles_primary_role",
        help_text="Primary professional role. option_set must be PROFESSIONAL_ROLE.",
    )
    additional_roles = models.JSONField(
        default=list, blank=True, help_text="Additional professional roles."
    )
    summary_source = models.CharField(
        max_length=20,
        choices=SummarySource.choices,
        default=SummarySource.USER,
        help_text="Origin of current summary text.",
    )
    availability_status = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="professional_profiles_availability",
        help_text="Current availability. option_set must be AVAILABILITY_STATUS.",
    )
    available_from = models.DateField(
        null=True, blank=True, help_text="Date from which user is available."
    )
    notice_period_days = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Notice period in days (0-365)."
    )
    engagement_types = models.JSONField(
        default=list, blank=True, help_text="Preferred employment/contract types."
    )
    preferred_locations = models.JSONField(
        default=list, blank=True, help_text="Preferred work locations."
    )
    offshore_ready = models.BooleanField(
        default=False, help_text="Self-declared willingness/readiness for offshore work."
    )
    rate_type = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="professional_profiles_rate_type",
        help_text="Expected rate basis. option_set must be RATE_TYPE.",
    )
    expected_rate = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Expected base rate.",
    )
    rate_currency = models.CharField(
        max_length=3, blank=True, help_text="Currency of expected rate; required "
        "when expected_rate exists."
    )
    ppe_sizes = models.JSONField(
        default=dict,
        blank=True,
        help_text="PPE sizes for mobilisation; restricted PII; never used in resume.",
    )
    submitted_at = models.DateTimeField(
        null=True, blank=True, help_text="Stage 2 submission time."
    )
    approved_at = models.DateTimeField(
        null=True, blank=True, help_text="Profile approval time."
    )

    class Meta:
        db_table = "professionals_professional_profile"
        verbose_name = "Professional Profile"
        verbose_name_plural = "Professional Profiles"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "user"], name="uniq_professional_profile_tenant_user"
            ),
            models.CheckConstraint(
                check=Q(completion_percent__gte=0) & Q(completion_percent__lte=100),
                name="chk_professional_profile_completion_percent_range",
            ),
            models.CheckConstraint(
                check=(
                    Q(notice_period_days__isnull=True)
                    | (Q(notice_period_days__gte=0) & Q(notice_period_days__lte=365))
                ),
                name="chk_professional_profile_notice_period_range",
            ),
            models.CheckConstraint(
                check=(Q(expected_rate__isnull=True) | ~Q(rate_currency="")),
                name="chk_professional_profile_rate_currency_required",
            ),
            models.CheckConstraint(
                check=(
                    (Q(address_line_1="") & Q(address_line_2="") & Q(postal_code=""))
                    | ~Q(address_country_code="")
                ),
                name="chk_professional_profile_address_country_required",
            ),
            models.CheckConstraint(
                check=(
                    ~Q(classification_status="CONFIRMED") | Q(classified_at__isnull=False)
                ),
                name="chk_professional_profile_classified_at_required",
            ),
            models.CheckConstraint(
                check=~Q(classified_by=F("user")),
                name="chk_professional_profile_classified_by_not_owner",
            ),
        ]

    def __str__(self):
        return self.display_name or self.legal_full_name or str(self.user_id)


class ProfessionalReview(TenantOwnedModel, CreatedOnlyModel):
    """Append-only history of profile approval, system classification
    recommendation, Candidate/Mentor confirmation and reclassification.

    Key rules: System recommendation is not automatically final unless an
    explicit future policy enables it. Mentor classification cannot be
    based only on years. Final decisions are immutable.
    """

    class ReviewType(models.TextChoices):
        PROFILE_APPROVAL = "PROFILE_APPROVAL", "Profile approval"
        INITIAL_CLASSIFICATION = "INITIAL_CLASSIFICATION", "Initial classification"
        RECLASSIFICATION = "RECLASSIFICATION", "Reclassification"
        MATERIAL_UPDATE = "MATERIAL_UPDATE", "Material update"

    class Recommendation(models.TextChoices):
        CANDIDATE = "CANDIDATE", "Candidate"
        MENTOR = "MENTOR", "Mentor"
        INSUFFICIENT_DATA = "INSUFFICIENT_DATA", "Insufficient data"

    class Classification(models.TextChoices):
        UNCLASSIFIED = "UNCLASSIFIED", "Unclassified"
        CANDIDATE = "CANDIDATE", "Candidate"
        MENTOR = "MENTOR", "Mentor"

    class Decision(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        RETURNED = "RETURNED", "Returned"

    professional = models.ForeignKey(
        ProfessionalProfile,
        on_delete=models.CASCADE,
        related_name="reviews",
        db_index=True,
        help_text="Professional being reviewed.",
    )
    review_type = models.CharField(
        max_length=30, choices=ReviewType.choices, help_text="Type of professional review."
    )
    profile_version = models.PositiveIntegerField(
        help_text="Profile version reviewed; must equal a submitted profile version."
    )
    submitted_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        related_name="professional_reviews_submitted",
        help_text="User who submitted the review request. Usually profile owner.",
    )
    submitted_at = models.DateTimeField(help_text="Review submission timestamp.")
    system_recommendation = models.CharField(
        max_length=20,
        choices=Recommendation.choices,
        blank=True,
        help_text="Classification suggested by system rules.",
    )
    system_confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Confidence score for system suggestion (0.00-100.00).",
    )
    ruleset_version = models.CharField(
        max_length=30, blank=True, help_text="Ruleset version; required for system recommendation."
    )
    previous_classification = models.CharField(
        max_length=20,
        choices=Classification.choices,
        help_text="Classification before review.",
    )
    proposed_classification = models.CharField(
        max_length=20,
        choices=[
            (Classification.CANDIDATE, Classification.CANDIDATE.label),
            (Classification.MENTOR, Classification.MENTOR.label),
        ],
        blank=True,
        help_text="Proposed classification.",
    )
    decision = models.CharField(
        max_length=20,
        choices=Decision.choices,
        default=Decision.PENDING,
        db_index=True,
        help_text="Review decision.",
    )
    final_classification = models.CharField(
        max_length=20,
        choices=[
            (Classification.CANDIDATE, Classification.CANDIDATE.label),
            (Classification.MENTOR, Classification.MENTOR.label),
        ],
        blank=True,
        help_text="Final Candidate/Mentor decision; required when APPROVED.",
    )
    reviewed_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="professional_reviews_decided",
        help_text="Decision maker. Tenant Admin/Reviewer or Platform Super "
        "Admin; cannot be profile owner.",
    )
    reviewer_role_snapshot = models.CharField(
        max_length=60, blank=True, help_text="Reviewer role captured for audit."
    )
    decision_reason = models.TextField(
        max_length=3000,
        blank=True,
        help_text="Required for rejection, return or override of system recommendation.",
    )
    reviewer_notes = models.TextField(
        max_length=3000, blank=True, help_text="Internal only additional notes."
    )
    criteria_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="Evidence and criteria used in the decision; immutable after decision.",
    )
    decided_at = models.DateTimeField(
        null=True, blank=True, help_text="Decision timestamp; required when not PENDING."
    )

    class Meta:
        db_table = "professionals_professional_review"
        verbose_name = "Professional Review"
        verbose_name_plural = "Professional Reviews"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=(Q(system_recommendation="") | Q(system_confidence__isnull=False)),
                name="chk_professional_review_system_confidence_required",
            ),
            models.CheckConstraint(
                check=(Q(system_recommendation="") | ~Q(ruleset_version="")),
                name="chk_professional_review_ruleset_version_required",
            ),
            models.CheckConstraint(
                check=(~Q(decision="APPROVED") | ~Q(final_classification="")),
                name="chk_professional_review_final_classification_required",
            ),
            models.CheckConstraint(
                check=(Q(decision="PENDING") | Q(decided_at__isnull=False)),
                name="chk_professional_review_decided_at_required",
            ),
        ]

    def __str__(self):
        return f"{self.professional} — {self.review_type} ({self.decision})"


class CredentialRecord(TenantOwnedModel, TimeStampedModel, ArchivableModel):
    """Optimised repeatable table for education, certification, training,
    passport, visa/work permit, marine credentials, membership, publication,
    award, client approval and medical fitness.

    Key rules: Record-type-specific validation is applied in services.
    Expired/revoked records remain in history. Passport, visa and medical
    fields are encrypted/restricted and resume-hidden by default.
    """

    class RecordType(models.TextChoices):
        EDUCATION = "EDUCATION", "Education"
        CERTIFICATION = "CERTIFICATION", "Certification"
        TRAINING = "TRAINING", "Training"
        PASSPORT = "PASSPORT", "Passport"
        VISA_WORK_PERMIT = "VISA_WORK_PERMIT", "Visa / work permit"
        MARINE_CDC = "MARINE_CDC", "Marine CDC"
        MARINE_COC = "MARINE_COC", "Marine COC"
        MEMBERSHIP = "MEMBERSHIP", "Membership"
        PUBLICATION = "PUBLICATION", "Publication"
        AWARD = "AWARD", "Award"
        CLIENT_APPROVAL = "CLIENT_APPROVAL", "Client approval"
        MEDICAL_FITNESS = "MEDICAL_FITNESS", "Medical fitness"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        EXPIRED = "EXPIRED", "Expired"
        REVOKED = "REVOKED", "Revoked"
        ARCHIVED = "ARCHIVED", "Archived"

    professional = models.ForeignKey(
        ProfessionalProfile,
        on_delete=models.CASCADE,
        related_name="credentials",
        db_index=True,
        help_text="Professional who owns the record.",
    )
    record_type = models.CharField(
        max_length=30, choices=RecordType.choices, help_text="Credential category."
    )
    title = models.CharField(
        max_length=200,
        help_text="Qualification, certificate, document or recognition title.",
    )
    issuing_organization = models.ForeignKey(
        "tenancy.Organization",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="credentials_issued",
        help_text="Structured issuing body. Same tenant; type should match "
        "record context where known.",
    )
    issuing_body_snapshot = models.CharField(
        max_length=200,
        blank=True,
        help_text="Issuer name preserved as entered; required when no "
        "issuing_organization is selected.",
    )
    issuing_country_code = models.CharField(
        max_length=2,
        blank=True,
        validators=[validate_iso_country_code],
        help_text="Issuing country; required for passport and some "
        "travel/marine documents.",
    )
    discipline_or_field = models.CharField(
        max_length=160,
        blank=True,
        help_text="Academic or technical discipline; required for applicable "
        "education/certification records.",
    )
    level_or_grade = models.CharField(
        max_length=100,
        blank=True,
        help_text="Qualification grade, certification level or membership grade.",
    )
    credential_number = EncryptedCharField(
        max_length=120,
        blank=True,
        help_text="Certificate, passport, membership or approval number. "
        "Masked in API responses.",
    )
    start_date = models.DateField(
        null=True, blank=True, help_text="Education/training start date."
    )
    issue_date = models.DateField(
        null=True, blank=True, help_text="Issue/award/publication date."
    )
    expiry_date = models.DateField(
        null=True, blank=True, help_text="Expiry date; required for expiry-"
        "controlled types; status auto-updated."
    )
    end_date = models.DateField(
        null=True, blank=True, help_text="Education/training end date."
    )
    related_scope = models.ForeignKey(
        "catalog.ScopeCatalog",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="credentials",
        help_text="Related technical scope; used when credential supports "
        "a specific scope.",
    )
    related_project = models.ForeignKey(
        "experience.ProjectRecord",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="credentials",
        help_text="Related project; used for client approvals. Same "
        "tenant/professional.",
    )
    client_organization = models.ForeignKey(
        "tenancy.Organization",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="credentials_client_approved",
        help_text="Client/agency associated with approval.",
    )
    restrictions_or_limitations = models.TextField(
        max_length=1000,
        blank=True,
        help_text="Credential limitations, endorsements or medical restrictions. "
        "Restricted for medical and marine records.",
    )
    publication_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="Publication link; required for publication when no "
        "publisher evidence is provided.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        help_text="Current credential lifecycle status.",
    )
    verification_status = models.CharField(
        max_length=30,
        choices=VerificationStatus.choices,
        default=VerificationStatus.SELF_DECLARED,
        help_text="Verification state.",
    )
    resume_visibility = models.CharField(
        max_length=30,
        choices=ResumeVisibility.choices,
        default=ResumeVisibility.OPTIONAL,
        help_text="Resume inclusion rule; default by type, "
        "PASSPORT/VISA/MEDICAL = NEVER.",
    )
    data_classification = models.CharField(
        max_length=30,
        choices=DataClassification.choices,
        default=DataClassification.PROFESSIONAL,
        help_text="Privacy classification; default by type, sensitive "
        "types cannot be downgraded by user.",
    )
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Non-sensitive type-specific fields only; schema validated "
        "by record_type.",
    )
    secure_details = EncryptedTextField(
        null=True,
        blank=True,
        help_text="Restricted type-specific details; excluded from normal "
        "querysets and logs.",
    )

    class Meta:
        db_table = "professionals_credential_record"
        verbose_name = "Credential Record"
        verbose_name_plural = "Credential Records"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(start_date__isnull=True)
                    | Q(end_date__isnull=True)
                    | Q(start_date__lte=F("end_date"))
                ),
                name="chk_credential_record_start_before_end",
            ),
            models.CheckConstraint(
                check=(
                    Q(issue_date__isnull=True)
                    | Q(expiry_date__isnull=True)
                    | Q(issue_date__lte=F("expiry_date"))
                ),
                name="chk_credential_record_issue_before_expiry",
            ),
            models.CheckConstraint(
                check=(
                    Q(issuing_organization__isnull=False) | ~Q(issuing_body_snapshot="")
                ),
                name="chk_credential_record_issuing_body_required",
            ),
        ]

    def __str__(self):
        return f"{self.professional} — {self.title}"


class CapabilityRecord(TenantOwnedModel, TimeStampedModel):
    """Optimised supporting record for languages, codes/standards,
    equipment, software, digital tools and soft skills.

    Key rules: A standard/equipment/software capability may use a master
    value or approved custom value. Language keeps separate speaking,
    reading and writing levels.
    """

    class CapabilityType(models.TextChoices):
        LANGUAGE = "LANGUAGE", "Language"
        STANDARD = "STANDARD", "Standard"
        EQUIPMENT = "EQUIPMENT", "Equipment"
        SOFTWARE = "SOFTWARE", "Software"
        DIGITAL_TOOL = "DIGITAL_TOOL", "Digital tool"
        SOFT_SKILL = "SOFT_SKILL", "Soft skill"

    class Proficiency(models.TextChoices):
        AWARE = "AWARE", "Aware"
        SUPERVISED = "SUPERVISED", "Supervised"
        INDEPENDENT = "INDEPENDENT", "Independent"
        EXPERT = "EXPERT", "Expert"

    professional = models.ForeignKey(
        ProfessionalProfile,
        on_delete=models.CASCADE,
        related_name="capabilities",
        db_index=True,
        help_text="Professional who owns the capability.",
    )
    capability_type = models.CharField(
        max_length=25, choices=CapabilityType.choices, help_text="Capability category."
    )
    reference_value = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="capability_records",
        help_text="Platform-managed master value; option_set must match "
        "capability_type.",
    )
    custom_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Approved custom capability name; required when "
        "reference_value is NULL.",
    )
    related_scope = models.ForeignKey(
        "catalog.ScopeCatalog",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="capability_records",
        help_text="Optional scope where the capability applies.",
    )
    edition_or_model = models.CharField(
        max_length=100,
        blank=True,
        help_text="Standard edition or equipment make/model; recommended "
        "for standards and equipment.",
    )
    proficiency = models.CharField(
        max_length=30,
        choices=Proficiency.choices,
        blank=True,
        help_text="General proficiency level; not used as the only language level.",
    )
    speaking_level = models.CharField(
        max_length=30,
        blank=True,
        help_text="Speaking proficiency; required when capability_type=LANGUAGE.",
    )
    reading_level = models.CharField(
        max_length=30,
        blank=True,
        help_text="Reading proficiency; required when capability_type=LANGUAGE.",
    )
    writing_level = models.CharField(
        max_length=30,
        blank=True,
        help_text="Writing proficiency; required when capability_type=LANGUAGE.",
    )
    years_experience = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Approximate years using the capability; informational only.",
    )
    last_used_date = models.DateField(
        null=True,
        blank=True,
        validators=[validate_not_future_date],
        help_text="Most recent use date.",
    )
    verification_status = models.CharField(
        max_length=30,
        choices=VerificationStatus.choices,
        default=VerificationStatus.SELF_DECLARED,
        help_text="Verification state.",
    )
    resume_visibility = models.CharField(
        max_length=30,
        choices=ResumeVisibility.choices,
        default=ResumeVisibility.OPTIONAL,
        help_text="Resume inclusion rule.",
    )
    details = models.JSONField(
        default=dict, blank=True, help_text="Additional capability attributes; "
        "schema validated by capability_type."
    )

    class Meta:
        db_table = "professionals_capability_record"
        verbose_name = "Capability Record"
        verbose_name_plural = "Capability Records"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=(Q(reference_value__isnull=False) | ~Q(custom_name="")),
                name="chk_capability_record_custom_name_required",
            ),
            models.CheckConstraint(
                check=(
                    ~Q(capability_type="LANGUAGE")
                    | (~Q(speaking_level="") & ~Q(reading_level="") & ~Q(writing_level=""))
                ),
                name="chk_capability_record_language_levels_required",
            ),
            models.CheckConstraint(
                check=Q(years_experience__isnull=True) | Q(years_experience__gte=0),
                name="chk_capability_record_years_experience_non_negative",
            ),
        ]

    def __str__(self):
        return self.custom_name or str(self.reference_value_id)


class ContactRecord(TenantOwnedModel, TimeStampedModel):
    """Stores professional references and emergency contacts without
    mixing them with the professional identity record.

    Key rules: At least email or phone is required. Reference details
    cannot be shared without consent. Emergency contacts are never used
    in resumes.
    """

    class ContactType(models.TextChoices):
        PROFESSIONAL_REFERENCE = "PROFESSIONAL_REFERENCE", "Professional reference"
        EMERGENCY_CONTACT = "EMERGENCY_CONTACT", "Emergency contact"

    professional = models.ForeignKey(
        ProfessionalProfile,
        on_delete=models.CASCADE,
        related_name="contacts",
        db_index=True,
        help_text="Professional who owns the contact.",
    )
    contact_type = models.CharField(
        max_length=30, choices=ContactType.choices, help_text="Contact category."
    )
    full_name = models.CharField(
        max_length=160,
        validators=[MinLengthValidator(2)],
        help_text="Contact person name.",
    )
    job_title = models.CharField(
        max_length=120, blank=True, help_text="Contact job title; used mainly "
        "for professional references."
    )
    organization = models.ForeignKey(
        "tenancy.Organization",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="contact_records",
        help_text="Structured organisation reference.",
    )
    organization_name_snapshot = models.CharField(
        max_length=200,
        blank=True,
        help_text="Organisation name shown with contact; preserves entered name.",
    )
    relationship = models.CharField(
        max_length=100,
        blank=True,
        help_text="Relationship to professional; recommended for both contact types.",
    )
    email = models.EmailField(
        max_length=254, blank=True, help_text="Contact email; at least email or "
        "phone must be provided."
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[validate_e164_phone],
        help_text="Contact phone; at least email or phone required.",
    )
    consent_given = models.BooleanField(
        default=False, help_text="Must be true before reference details can be shared."
    )
    consent_given_at = models.DateTimeField(
        null=True, blank=True, help_text="Required when consent_given=true."
    )
    verification_status = models.CharField(
        max_length=30,
        choices=VerificationStatus.choices,
        default=VerificationStatus.SELF_DECLARED,
        help_text="Verification state.",
    )
    resume_visibility = models.CharField(
        max_length=30,
        choices=ResumeVisibility.choices,
        help_text="Resume inclusion rule. Reference default=CLIENT_SPECIFIC; "
        "emergency=NEVER — set explicitly per contact_type.",
    )
    data_classification = models.CharField(
        max_length=30,
        choices=DataClassification.choices,
        help_text="Privacy classification. Reference=SENSITIVE_PII; "
        "emergency=RESTRICTED_PII — set explicitly per contact_type.",
    )

    class Meta:
        db_table = "professionals_contact_record"
        verbose_name = "Contact Record"
        verbose_name_plural = "Contact Records"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=(~Q(email="") | ~Q(phone="")),
                name="chk_contact_record_email_or_phone_required",
            ),
            models.CheckConstraint(
                check=(Q(consent_given=False) | Q(consent_given_at__isnull=False)),
                name="chk_contact_record_consent_given_at_required",
            ),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.contact_type})"

