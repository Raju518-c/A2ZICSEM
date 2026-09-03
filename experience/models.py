"""experience: employment, projects, project scopes, dynamic scope
responses, date-level exposure logs and dated professional assignments.

Ownership and access: Professional enters records. Tenant reviewers
verify. Tenant Admin manages organisational, project, rotation and mentor
assignments.
"""

import uuid

from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import F, Q

from core.choices import CompletionStatus, RecordStatus, ResumeVisibility, VerificationStatus
from core.models import TenantOwnedModel, TimeStampedModel, UUIDModel


class EmploymentRecord(TenantOwnedModel, TimeStampedModel):
    """Stores chronological employment history used for professional
    profile and resume output.

    Key rules: Overlapping employment is allowed but flagged. Total
    experience is calculated using the union of valid date intervals, not
    a raw sum.
    """

    professional = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.CASCADE,
        related_name="employment_records",
        db_index=True,
        help_text="Professional who owns the employment record.",
    )
    # employer_organization = models.ForeignKey(
    #     "tenancy.Organization",
    #     on_delete=models.PROTECT,
    #     null=True,
    #     blank=True,
    #     related_name="employment_records",
    #     help_text="Structured employer. Same tenant; employer type recommended.",
    # )
    employer_organization = models.CharField(
        max_length=200, null=True, blank=True, help_text="Structured employer. Same tenant; employer type recommended."
    )
    
    employer_name_snapshot = models.CharField(
        max_length=200,
        help_text="Employer name preserved for history/resume; required even "
        "if employer_organization exists.",
    )
    job_title = models.CharField(
        max_length=160,
        validators=[MinLengthValidator(2)],
        help_text="Employment job title.",
    )
    employment_type = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="employment_records",
        help_text="Permanent, contract, rotation, freelance, etc. "
        "option_set must be ENGAGEMENT_TYPE.",
    )
    
    # industry_classification = models.ForeignKey(
    #     "catalog.referencevalue",
    #     on_delete=models.PROTECT,
    #     null=True,
    #     blank=True,
    #     related_name="project_records",
    #     help_text="Related industry; used for classification and reporting.",
    # )
    
    # scope = models.ForeignKey(
    #     "catalog.ScopeCatalog",
    #     on_delete=models.PROTECT,
    #     related_name="project_scopes",
    #     db_index=True,
    #     help_text="Scope performed on project; active scope, registration "
    #     "industry does not limit later verified scopes.",
    # )
    
    country_code = models.CharField(max_length=2, blank=True, help_text="Employment country.")
    city = models.CharField(max_length=120, blank=True, help_text="Employment city.")
    start_date = models.DateField(help_text="Employment start date; cannot be after end_date.")
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Employment end date; required unless is_current=true; on/after start_date.",
    )
    is_current = models.BooleanField(
        default=False,
        help_text="Current employment flag. If true, end_date must be NULL; "
        "if false, end_date required.",
    )
    duties = models.TextField(max_length=3000, blank=True, help_text="Main duties.")
    verification_status = models.CharField(
        max_length=30,
        choices=VerificationStatus.choices,
        default=VerificationStatus.SELF_DECLARED,
        help_text="Verification state.",
    )
    evidence = models.ForeignKey(
        "evidence.EvidenceDocument",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employement_records",
        help_text=(
            "Primary supporting document. "
            "Must belong to same professional."
        ),
    )
    resume_visibility = models.CharField(
        max_length=30,
        choices=ResumeVisibility.choices,
        default=ResumeVisibility.ALWAYS,
        help_text="Resume inclusion rule.",
    )
    status = models.CharField(
        max_length=20,
        choices=RecordStatus.choices,
        default=RecordStatus.DRAFT,
        db_index=True,
        help_text="Record lifecycle status.",
    )

    class Meta:
        db_table = "experience_employment_record"
        verbose_name = "EmploymentRecord"
        verbose_name_plural = "EmploymentRecord"
        ordering = ["-start_date"]
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(end_date__isnull=True) | Q(start_date__lte=F("end_date"))
                ),
                name="chk_employment_record_start_before_end",
            ),
            models.CheckConstraint(
                check=(
                    (Q(is_current=True) & Q(end_date__isnull=True))
                    | (Q(is_current=False) & Q(end_date__isnull=False))
                ),
                name="chk_employment_record_is_current_end_date_consistency",
            ),
        ]

    def __str__(self):
        return f"{self.professional} — {self.job_title} @ {self.employer_name_snapshot}"


class ProjectRecord(TenantOwnedModel, TimeStampedModel, UUIDModel):
    """Main structured project-experience record and primary source for
    resume responsibilities, achievements, standards and experience
    calculations.

    Key rules: Concurrent allocations above 100% block verification.
    Project outside linked employment requires explanation. Confidential
    client names are redaction-scanned in all free text.
    """

    class ClientVisibility(models.TextChoices):
        SHOW_CLIENT_NAME = "SHOW_CLIENT_NAME", "Show client name"
        SHOW_MASKED_CLIENT_CATEGORY = (
            "SHOW_MASKED_CLIENT_CATEGORY",
            "Show masked client category",
        )
        CONFIDENTIAL_DO_NOT_DISPLAY = (
            "CONFIDENTIAL_DO_NOT_DISPLAY",
            "Confidential — do not display",
        )

    class WorkingArrangement(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full time"
        ROTATION = "ROTATION", "Rotation"
        PART_TIME = "PART_TIME", "Part time"
        FREELANCE = "FREELANCE", "Freelance"

    professional = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.CASCADE,
        related_name="project_records",
        db_index=True,
        help_text="Professional who performed the project.",
    )
    employment = models.ForeignKey(
        EmploymentRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_records",
        help_text="Employment/contract under which project was performed. "
        "Must belong to same professional; dates normally cover project.",
    )
    project_name = models.CharField(max_length=220, help_text="Project name.")
    # employer_organization = models.ForeignKey(
    #     "tenancy.Organization",
    #     on_delete=models.PROTECT,
    #     null=True,
    #     blank=True,
    #     related_name="project_records_as_employer",
    #     help_text="Employer/contracting organisation for project.",
    # )
    employer_organization = models.CharField(
        max_length=200, null=True, blank=True, help_text="Structured employer. Same tenant; employer type recommended."
    )
    # client_organization = models.ForeignKey(
    #     "tenancy.Organization",
    #     on_delete=models.PROTECT,
    #     null=True,
    #     blank=True,
    #     related_name="project_records_as_client",
    #     help_text="Structured client organisation. Same tenant; CLIENT type recommended.",
    # )
    client_organization = models.CharField(
        max_length=200, null=True, blank=True, help_text="Structured client. Same tenant; client type recommended."
    )
    client_name_snapshot = models.CharField(
        max_length=200,
        help_text="Client name as recorded for project; retained even if "
        "organisation renamed.",
    )
    # client_alias = models.CharField(
    #     max_length=200,
    #     blank=True,
    #     help_text="Safe client alias, e.g. Confidential International EPC "
    #     "Client. Required when visibility is masked and an alias is used.",
    # )
    client_visibility = models.CharField(
        max_length=40,
        choices=ClientVisibility.choices,
        default=ClientVisibility.SHOW_CLIENT_NAME,
        help_text="Client confidentiality rule.",
    )
    country_code = models.CharField(max_length=2, blank=True, help_text="Project country.")
    city = models.CharField(max_length=120, blank=True, help_text="Project city/location.")
    role_title = models.ForeignKey('catalog.ReferenceValue', on_delete=models.PROTECT, null=True, blank=True, 
        related_name='project_records_as_role', help_text='Role performed on project; option_set must be ROLE_TITLE.'
    )
    # role_title = models.CharField(max_length=160, help_text="Role performed on project.")
    start_date = models.DateField(help_text="Project start date; cannot be after end_date.")
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Project end date; required unless is_current=true; on/after start_date.",
    )
    is_current = models.BooleanField(default=False, help_text="Current project flag.")
    allocation_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100,
        help_text="Time allocation during the project period; >0 and <=100.",
    )
    is_primary_assignment = models.BooleanField(
        default=True,
        help_text="Primary assignment indicator; normally at most one primary "
        "full-time assignment for overlapping period.",
    )
    working_arrangement = models.CharField(
        max_length=50, choices=WorkingArrangement.choices, blank=True,
        help_text="Working arrangement.",
    )
    engagement_explanation = models.TextField(
        max_length=1000,
        blank=True,
        help_text="Explanation for direct/freelance or chronology exception; "
        "required when project dates are outside linked employment/contract.",
    )
    declared_field_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Candidate-entered field-day estimate; self-declared only.",
    )
    verified_field_days = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text="Cached verified field days; derived from approved ExposureLog.",
    )
    responsibilities = models.TextField(
        max_length=3000,
        blank=True,
        validators=[MinLengthValidator(100)],
        help_text="Responsibilities and duties; 100-3000 characters, "
        "required at project submission.",
    )
    achievements = models.TextField(
        max_length=1500, blank=True, help_text="Key achievements."
    )
    achievement_evidence = models.ForeignKey(
        "evidence.EvidenceDocument",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="achievement_evidence",
        help_text=(
            "Primary supporting document. "
            "Must belong to same professional."
        ),
    )
    #evidence required for achievements 
    standards_applied = models.JSONField(
        default=list,
        blank=True,
        help_text="Codes and standards applied; list of standard reference "
        "IDs/codes and optional edition; no duplicates.",
    )
    verification_status = models.CharField(
        max_length=30,
        choices=VerificationStatus.choices,
        default=VerificationStatus.SELF_DECLARED,
        help_text="Verification state.",
    )
    verification_status_evidence = models.ForeignKey(
        "evidence.EvidenceDocument",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verification_status_evidence",
        help_text=(
            "Primary supporting document. "
            "Must belong to same professional."
        ),
    )
    #evidence required for verification_status 
    status = models.CharField(
        max_length=20,
        choices=CompletionStatus.choices,
        default=CompletionStatus.DRAFT,
        db_index=True,
        help_text="Record completion status.",
    )
    Experience_classification = models.CharField(
        max_length=30, null=True, blank=True, 
        choices=[("Technical", "Technical"), ("Non-Technical/Administrative", "Non-Technical/Administrative"), ("Employement only", "Employement only")], 
       help_text="Experience classification."
    )
    
    industry_classification = models.ForeignKey(
        "catalog.referencevalue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="project_records",
        help_text="Related industry; used for classification and reporting.",
    )

    class Meta:
        db_table = "experience_project_record"
        verbose_name = "ProjectRecord"
        verbose_name_plural = "ProjectRecord"
        ordering = ["-start_date"]
        constraints = [
            models.CheckConstraint(
                check=(Q(end_date__isnull=True) | Q(start_date__lte=F("end_date"))),
                name="chk_project_record_start_before_end",
            ),
            models.CheckConstraint(
                check=(
                    (Q(is_current=True) & Q(end_date__isnull=True))
                    | (Q(is_current=False) & Q(end_date__isnull=False))
                ),
                name="chk_project_record_is_current_end_date_consistency",
            ),
            models.CheckConstraint(
                check=Q(allocation_percent__gt=0) & Q(allocation_percent__lte=100),
                name="chk_project_record_allocation_percent_range",
            ),
            # models.CheckConstraint(
            #     check=(
            #         ~Q(client_visibility="SHOW_MASKED_CLIENT_CATEGORY")
            #         | ~Q(client_alias="")
            #     ),
            #     name="chk_project_record_client_alias_required",
            # ),
        ]

    def __str__(self):
        return f"{self.project_name} — {self.professional}"


class ProjectScope(TenantOwnedModel, TimeStampedModel):
    """Links one project to each inspection/survey scope performed and
    records the authority action exercised for that scope.

    Key rules: Unique project+scope. Authority action cannot exceed
    verified credentials, client approval or ProfessionalScope authority.
    """

    project = models.ForeignKey(
        ProjectRecord,
        on_delete=models.CASCADE,
        related_name="project_scopes",
        db_index=True,
        help_text="Owning project. Must equal project.tenant.",
    )
    scope = models.ForeignKey(
        "catalog.ScopeCatalog",
        on_delete=models.PROTECT,
        related_name="project_scopes",
        db_index=True,
        help_text="Scope performed on project; active scope, registration "
        "industry does not limit later verified scopes.",
    )
    activity_summary = models.CharField(
        max_length=600, blank=True, help_text="Short description of scope activity."
    )
    authority_action = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="project_scopes",
        help_text="Observed, assisted, performed, reviewed, approved, etc. "
        "option_set must be AUTHORITY_ACTION.",
    )
    verification_status = models.CharField(
        max_length=30,
        choices=VerificationStatus.choices,
        default=VerificationStatus.SELF_DECLARED,
        help_text="Verification state.",
    )
    status = models.CharField(
        max_length=20,
        choices=CompletionStatus.choices,
        default=CompletionStatus.DRAFT,
        db_index=True,
        help_text="Completion status.",
    )

    class Meta:
        db_table = "experience_project_scope"
        verbose_name = "ProjectScope"
        verbose_name_plural = "ProjectScope"
        ordering = ["project", "scope"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "scope"], name="uniq_project_scope_project_scope"
            ),
        ]

    def __str__(self):
        return f"{self.project} — {self.scope}"


class ScopeResponse(TenantOwnedModel, TimeStampedModel):
    """Stores answers to the dynamic FormFields activated for a ProjectScope.

    Key rules: Answer JSON must match FormField data type and validation
    schema. Verified answers return to review when materially changed.
    Repeat fields use group key and index.
    """

    project_scope = models.ForeignKey(
        ProjectScope,
        on_delete=models.CASCADE,
        related_name="scope_responses",
        db_index=True,
        help_text="Project-scope answer set. Must equal project_scope.tenant.",
    )
    form_field = models.ForeignKey(
        "catalog.FormField",
        on_delete=models.PROTECT,
        related_name="scope_responses",
        db_index=True,
        help_text="Question being answered; must belong to an active module "
        "mapped to project_scope.scope.",
    )
    repeat_group_key = models.UUIDField(
        default=uuid.uuid4,
        help_text="Groups repeated fields into one logical record. "
        "Non-repeatable fields use one standard group; repeatable fields "
        "may use many.",
    )
    repeat_index = models.PositiveSmallIntegerField(
        default=0, help_text="Order within repeated group."
    )
    value = models.JSONField(
        null=True,
        blank=True,
        help_text="Actual answer value; must pass FormField.data_type, "
        "options and validation_schema.",
    )
    verification_status = models.CharField(
        max_length=30,
        choices=VerificationStatus.choices,
        default=VerificationStatus.SELF_DECLARED,
        help_text="Answer verification state.",
    )
    verified_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="scope_responses_verified",
        help_text="Verifier; authorised same-tenant reviewer; cannot verify "
        "own answer where separation is required.",
    )
    verified_at = models.DateTimeField(
        null=True, blank=True, help_text="Required when verification status "
        "is verified/validated."
    )

    class Meta:
        db_table = "experience_scope_response"
        verbose_name = "ScopeResponse"
        verbose_name_plural = "ScopeResponse"
        ordering = ["project_scope", "form_field", "repeat_group_key", "repeat_index"]
        constraints = [            
            models.CheckConstraint(
                check=(
                    ~Q(verification_status__in=["VERIFIED", "VALIDATED"])
                    | Q(verified_at__isnull=False)
                ),
                name="chk_scope_response_verified_at_required",
            ),
        ]

    def __str__(self):
        return f"{self.project_scope} — {self.form_field}"


class ExposureLog(TenantOwnedModel, TimeStampedModel):
    """Date-level digital logbook used to calculate verified field/site
    days without double counting overlapping projects.

    Key rules: Approved day fractions for one professional/date normally
    cannot exceed 1.00. Rejected or draft logs are excluded from
    competency calculations.
    """

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    professional = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.CASCADE,
        related_name="exposure_logs",
        db_index=True,
        help_text="Professional whose exposure is logged. Must equal "
        "project_scope.project.professional.",
    )
    project_scope = models.ForeignKey(
        ProjectScope,
        on_delete=models.CASCADE,
        related_name="exposure_logs",
        db_index=True,
        help_text="Project and scope for the activity. Same professional and tenant.",
    )
    activity_date = models.DateField(
        help_text="Date of field/site activity; normally within project dates."
    )
    hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Hours worked/exposed; greater than 0 and <=24.",
    )
    day_fraction = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1,
        help_text="Fraction of one verified day; greater than 0 and <=1.",
    )
    site_or_asset = models.CharField(
        max_length=200, blank=True, help_text="Plant, yard, vessel, site or asset."
    )
    activity_summary = models.TextField(
        max_length=2000, help_text="Summary of activity and learning/execution."
    )
    supervisor_professional = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="exposure_logs_supervised",
        help_text="Supervisor/mentor associated with log. Same tenant; "
        "cannot equal professional.",
    )
    verification_status = models.CharField(
        max_length=30,
        choices=VerificationStatus.choices,
        default=VerificationStatus.SELF_DECLARED,
        help_text="Evidence/validation state.",
    )
    verified_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="exposure_logs_verified",
        help_text="Approver/verifier; authorised mentor/reviewer; cannot be "
        "the same user where self-verification is prohibited.",
    )
    verified_at = models.DateTimeField(
        null=True, blank=True, help_text="Required for approved/verified status."
    )
    review_notes = models.TextField(
        max_length=2000, blank=True, help_text="Review comments."
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        help_text="Log workflow status.",
    )

    class Meta:
        db_table = "experience_exposure_log"
        verbose_name = "ExposureLog"
        verbose_name_plural = "ExposureLog"
        ordering = ["-activity_date"]
        constraints = [
            models.CheckConstraint(
                check=Q(hours__isnull=True) | (Q(hours__gt=0) & Q(hours__lte=24)),
                name="chk_exposure_log_hours_range",
            ),
            models.CheckConstraint(
                check=Q(day_fraction__gt=0) & Q(day_fraction__lte=1),
                name="chk_exposure_log_day_fraction_range",
            ),
            models.CheckConstraint(
                check=~Q(supervisor_professional=F("professional")),
                name="chk_exposure_log_supervisor_not_self",
            ),
            models.CheckConstraint(
                check=(
                    ~Q(verification_status__in=["VERIFIED", "VALIDATED"])
                    | Q(verified_at__isnull=False)
                ),
                name="chk_exposure_log_verified_at_required",
            ),
        ]

    def __str__(self):
        return f"{self.professional} — {self.activity_date}"


class ProfessionalAssignment(TenantOwnedModel, TimeStampedModel):
    """Stores dated assignments to branches, departments, operating units,
    projects, training rotations, mentors and technical-review
    responsibilities.

    Key rules: Users are not permanently linked to department/branch on
    User. Assignment history is closed with end_date/status, not
    overwritten or deleted.
    """

    class AssignmentType(models.TextChoices):
        BRANCH = "BRANCH", "Branch"
        DEPARTMENT = "DEPARTMENT", "Department"
        OPERATING_UNIT = "OPERATING_UNIT", "Operating unit"
        TRAINING_ROTATION = "TRAINING_ROTATION", "Training rotation"
        PROJECT = "PROJECT", "Project"
        MENTOR = "MENTOR", "Mentor"
        TECHNICAL_REVIEW = "TECHNICAL_REVIEW", "Technical review"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    professional = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.CASCADE,
        related_name="assignments",
        db_index=True,
        help_text="Professional receiving the assignment.",
    )
    assignment_type = models.CharField(
        max_length=30, choices=AssignmentType.choices, help_text="Type of assignment."
    )
    organization = models.ForeignKey(
        "tenancy.Organization",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="professional_assignments",
        help_text="Assigned organisation unit; required for branch/department/"
        "operating-unit assignments and type must match.",
    )
    project = models.ForeignKey(
        ProjectRecord,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="professional_assignments",
        help_text="Assigned project; required for project/technical-review "
        "assignments; same tenant.",
    )
    scope = models.ForeignKey(
        "catalog.ScopeCatalog",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="professional_assignments",
        help_text="Optional scope for technical or mentor assignment.",
    )
    mentor_professional = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="mentor_assignments",
        help_text="Assigned mentor; required for MENTOR assignment; must be "
        "confirmed Mentor; cannot equal professional.",
    )
    start_date = models.DateField(help_text="Assignment start; cannot be after end_date.")
    end_date = models.DateField(
        null=True, blank=True, help_text="Assignment end; must be on/after start_date."
    )
    allocation_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Allocation to assignment; greater than 0 and <=100.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text="Assignment status.",
    )
    assigned_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        related_name="professional_assignments_created",
        help_text="User who created the assignment. Same-tenant Tenant "
        "Admin or authorised reviewer.",
    )
    notes = models.TextField(max_length=2000, blank=True, help_text="Assignment notes.")

    class Meta:
        db_table = "experience_professional_assignment"
        verbose_name = "ProfessionalAssignment"
        verbose_name_plural = "ProfessionalAssignment"
        ordering = ["-start_date"]
        constraints = [
            models.CheckConstraint(
                check=(Q(end_date__isnull=True) | Q(start_date__lte=F("end_date"))),
                name="chk_professional_assignment_start_before_end",
            ),
            models.CheckConstraint(
                check=(
                    Q(allocation_percent__isnull=True)
                    | (Q(allocation_percent__gt=0) & Q(allocation_percent__lte=100))
                ),
                name="chk_professional_assignment_allocation_percent_range",
            ),
            models.CheckConstraint(
                check=~Q(mentor_professional=F("professional")),
                name="chk_professional_assignment_mentor_not_self",
            ),
            models.CheckConstraint(
                check=(
                    ~Q(assignment_type__in=["BRANCH", "DEPARTMENT", "OPERATING_UNIT"])
                    | Q(organization__isnull=False)
                ),
                name="chk_professional_assignment_organization_required",
            ),
            models.CheckConstraint(
                check=(
                    ~Q(assignment_type__in=["PROJECT", "TECHNICAL_REVIEW"])
                    | Q(project__isnull=False)
                ),
                name="chk_professional_assignment_project_required",
            ),
            models.CheckConstraint(
                check=(~Q(assignment_type="MENTOR") | Q(mentor_professional__isnull=False)),
                name="chk_professional_assignment_mentor_required",
            ),
        ]

    def __str__(self):
        return f"{self.professional} — {self.assignment_type}"
