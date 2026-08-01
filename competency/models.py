"""competency: current Qualion level and authority per scope, plus the
full assessment/progression history.

Ownership and access: System calculates experience metrics. Authorised
mentors/reviewers recommend. Tenant Admin/technical authority approves
according to policy.
"""

from django.conf import settings
from django.db import models
from django.db.models import Q

from core.choices import VerificationStatus
from core.models import CreatedOnlyModel, TenantOwnedModel, TimeStampedModel


class ProfessionalScope(TenantOwnedModel, TimeStampedModel):
    """Current competency summary for one Professional + Scope. Holds
    calculated experience and the current L0-L5/authority result.

    Key rules: Unique professional+scope. Experience values are
    system-managed. Level is never assigned from years alone and changes
    require an approved CompetencyAssessment.
    """

    professional = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.CASCADE,
        related_name="scopes",
        db_index=True,
        help_text="Professional being evaluated.",
    )
    scope = models.ForeignKey(
        "catalog.ScopeCatalog",
        on_delete=models.PROTECT,
        related_name="professional_scopes",
        db_index=True,
        help_text="Industry/scope competency context; global active/retired scope.",
    )
    calendar_experience_months = models.PositiveIntegerField(
        default=0,
        help_text="Non-duplicated calendar experience; union of verified "
        "project date intervals for this scope; never manually edited.",
    )
    verified_field_days = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text="Verified actual field exposure; derived from approved ExposureLog.",
    )
    complexity_rating = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="professional_scopes_complexity",
        help_text="Complexity of verified exposure; option_set must be "
        "COMPLEXITY; reviewer-assigned.",
    )
    current_qualion_level = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        related_name="professional_scopes_qualion_level",
        help_text="Current L0-L5 level for this scope; option_set must be "
        "QUALION_LEVEL; default L0.",
    )
    current_authority_status = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        related_name="professional_scopes_authority_status",
        help_text="Current permitted authority for this scope; option_set "
        "must be AUTHORITY_STATUS; default Observer.",
    )
    is_deployable = models.BooleanField(
        default=False,
        help_text="Derived from level, authority, valid credentials and compliance.",
    )
    verification_status = models.CharField(
        max_length=30,
        choices=VerificationStatus.choices,
        default=VerificationStatus.UNDER_REVIEW,
        help_text="Competency verification state.",
    )
    effective_from = models.DateField(
        null=True, blank=True, help_text="Effective date of current state."
    )
    last_recalculated_at = models.DateTimeField(
        null=True, blank=True, help_text="Updated after experience recalculation."
    )
    last_assessed_at = models.DateTimeField(
        null=True, blank=True, help_text="Set after approved assessment."
    )

    class Meta:
        db_table = "competency_professional_scope"
        verbose_name = "Professional Scope"
        verbose_name_plural = "Professional Scopes"
        ordering = ["professional", "scope"]
        constraints = [
            models.UniqueConstraint(
                fields=["professional", "scope"],
                name="uniq_professional_scope_professional_scope",
            ),
        ]

    def __str__(self):
        return f"{self.professional} — {self.scope}"


class CompetencyAssessment(TenantOwnedModel, CreatedOnlyModel):
    """Append-only evidence-based assessment history for level
    progression, revalidation and authority decisions.

    Key rules: A professional cannot assess or approve themselves. Ethics
    or documentation/evidence below configured threshold blocks
    progression. Approved records are immutable.
    """

    class AssessmentType(models.TextChoices):
        INITIAL = "INITIAL", "Initial"
        PERIODIC = "PERIODIC", "Periodic"
        PROGRESSION = "PROGRESSION", "Progression"
        AUTHORITY = "AUTHORITY", "Authority"
        REVALIDATION = "REVALIDATION", "Revalidation"

    class Decision(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    professional_scope = models.ForeignKey(
        ProfessionalScope,
        on_delete=models.CASCADE,
        related_name="assessments",
        db_index=True,
        help_text="Scope competency being assessed.",
    )
    assessment_type = models.CharField(
        max_length=30, choices=AssessmentType.choices, help_text="Assessment purpose."
    )
    assessor = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        related_name="competency_assessments_conducted",
        help_text="Person conducting assessment; authorised same-tenant "
        "reviewer/mentor; cannot be assessed professional.",
    )
    assessor_role_snapshot = models.CharField(
        max_length=60, help_text="Assessor authority snapshot captured at assessment time."
    )
    technical_knowledge_score = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Technical knowledge dimension (0.00-100.00)."
    )
    field_execution_score = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Field execution discipline dimension (0.00-100.00)."
    )
    documentation_evidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Documentation and evidence quality dimension; threshold "
        "may block progression.",
    )
    ethics_independence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Ethics and independence dimension; threshold may block progression.",
    )
    communication_conduct_score = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Communication and professional conduct dimension."
    )
    previous_level = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        related_name="competency_assessments_previous_level",
        help_text="Level before assessment; QUALION_LEVEL snapshot.",
    )
    recommended_level = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="competency_assessments_recommended_level",
        help_text="Assessor recommendation; QUALION_LEVEL.",
    )
    approved_level = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="competency_assessments_approved_level",
        help_text="Approved level; required when decision=APPROVED.",
    )
    previous_authority = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        related_name="competency_assessments_previous_authority",
        help_text="Authority before assessment; AUTHORITY_STATUS snapshot.",
    )
    recommended_authority = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="competency_assessments_recommended_authority",
        help_text="Recommended authority; AUTHORITY_STATUS.",
    )
    approved_authority = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="competency_assessments_approved_authority",
        help_text="Approved authority; required when decision=APPROVED.",
    )
    recommendation = models.TextField(
        max_length=3000, help_text="Assessor recommendation and observations; evidence-based."
    )
    decision = models.CharField(
        max_length=20,
        choices=Decision.choices,
        default=Decision.DRAFT,
        db_index=True,
        help_text="Assessment decision state.",
    )
    decision_reason = models.TextField(
        max_length=3000,
        blank=True,
        help_text="Required for rejection or override.",
    )
    approved_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="competency_assessments_approved",
        help_text="Final approver; authorised approver; cannot be assessed "
        "professional; separation of duties where configured.",
    )
    approved_at = models.DateTimeField(
        null=True, blank=True, help_text="Required when decision=APPROVED/REJECTED."
    )
    evidence_summary = models.JSONField(
        default=dict,
        blank=True,
        help_text="Evidence used in assessment; source record IDs and "
        "calculated metrics; immutable after decision.",
    )
    assessed_at = models.DateTimeField(help_text="Assessment date/time.")

    class Meta:
        db_table = "competency_assessment"
        verbose_name = "Competency Assessment"
        verbose_name_plural = "Competency Assessments"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=Q(technical_knowledge_score__gte=0) & Q(technical_knowledge_score__lte=100),
                name="chk_competency_assessment_technical_score_range",
            ),
            models.CheckConstraint(
                check=Q(field_execution_score__gte=0) & Q(field_execution_score__lte=100),
                name="chk_competency_assessment_field_execution_score_range",
            ),
            models.CheckConstraint(
                check=Q(documentation_evidence_score__gte=0)
                & Q(documentation_evidence_score__lte=100),
                name="chk_competency_assessment_documentation_score_range",
            ),
            models.CheckConstraint(
                check=Q(ethics_independence_score__gte=0) & Q(ethics_independence_score__lte=100),
                name="chk_competency_assessment_ethics_score_range",
            ),
            models.CheckConstraint(
                check=Q(communication_conduct_score__gte=0)
                & Q(communication_conduct_score__lte=100),
                name="chk_competency_assessment_communication_score_range",
            ),
            models.CheckConstraint(
                check=(~Q(decision="APPROVED") | Q(approved_level__isnull=False)),
                name="chk_competency_assessment_approved_level_required",
            ),
            models.CheckConstraint(
                check=(~Q(decision="APPROVED") | Q(approved_authority__isnull=False)),
                name="chk_competency_assessment_approved_authority_required",
            ),
            models.CheckConstraint(
                check=(~Q(decision="REJECTED") | ~Q(decision_reason="")),
                name="chk_competency_assessment_decision_reason_required",
            ),
            models.CheckConstraint(
                check=(~Q(decision__in=["APPROVED", "REJECTED"]) | Q(approved_at__isnull=False)),
                name="chk_competency_assessment_approved_at_required",
            ),
        ]

    def __str__(self):
        return f"{self.professional_scope} — {self.assessment_type} ({self.decision})"
