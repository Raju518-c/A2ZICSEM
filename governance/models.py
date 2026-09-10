"""governance: cross-application audit trail for sensitive,
administrative, verification and approval actions.

Ownership and access: System-generated and append-only. Platform Super
Admin can view all; Tenant Admin views only their tenant.
"""

import uuid

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import F, Q
from core.choices import PublicationStatus
from core.models import (
    ArchivableModel,
    CreatedOnlyModel,
    TenantOwnedModel,
    TimeStampedModel,
    UUIDModel,
)


class AuditEvent(models.Model):
    """Append-only audit event with actor, action, target, masked
    before/after values and request context.

    Key rules: Passwords, OTPs, tokens, full passport numbers and detailed
    medical data are never stored in audit JSON. Tenant is NULL only for
    platform-level actions.
    """

    tenant = models.ForeignKey(
        "tenancy.Tenant",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="audit_events",
        db_index=True,
        help_text="Tenant context; NULL only for platform-level action.",
    )
    actor = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
        db_index=True,
        help_text="User performing action; NULL for system tasks; same "
        "tenant unless platform action.",
    )
    actor_role_snapshot = models.CharField(
        max_length=80, blank=True, help_text="Role/permission context of actor captured at event time."
    )
    action = models.CharField(
        max_length=80,
        help_text="Action performed; controlled action codes such as "
        "CREATE_TENANT, APPROVE_USER, VERIFY, CLASSIFY, ASSESS, GENERATE_RESUME.",
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name="audit_events",
        help_text="Target model; restricted allow-list.",
    )
    object_id = models.PositiveBigIntegerField(help_text="Target row identifier.")
    before_data = models.JSONField(
        null=True, blank=True, help_text="State before change; sensitive values masked; size-limited."
    )
    after_data = models.JSONField(
        null=True, blank=True, help_text="State after change; sensitive values masked; size-limited."
    )
    reason = models.TextField(
        max_length=3000,
        blank=True,
        help_text="Business reason; required for override, rejection, "
        "suspension and revocation actions.",
    )
    correlation_id = models.UUIDField(
        default=uuid.uuid4,
        db_index=True,
        help_text="Workflow correlation identifier; shared by events in one "
        "transaction/workflow.",
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, help_text="Request IP address."
    )
    user_agent = models.TextField(
        max_length=1000, blank=True, help_text="Sanitised and length-limited "
        "request client information."
    )
    occurred_at = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text="Event timestamp; append-only."
    )

    class Meta:
        db_table = "governance_audit_event"
        verbose_name = "AuditEvent"
        verbose_name_plural = "AuditEvent"
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.action} — {self.content_type} #{self.object_id}"





class CalculatedFieldCode(models.TextChoices):
    """Controlled catalog of the 15 system-calculated fields. Keeps
    reporting/policy lookups (e.g. "requires four-eyes approval")
    independent of the free-text field_name on the target model.
    """

    CALENDAR_EXPERIENCE = "CALENDAR_EXPERIENCE", "Calendar experience"
    VERIFIED_FIELD_DAYS = "VERIFIED_FIELD_DAYS", "Verified field days"
    VERIFIED_PROJECT_COUNT = "VERIFIED_PROJECT_COUNT", "Verified project count"
    HIGHEST_AUTHORITY_REACHED = "HIGHEST_AUTHORITY_REACHED", "Highest authority reached"
    QUALION_LEVEL = "QUALION_LEVEL", "Qualion level (L0-L5)"
    PROFESSIONAL_HEADLINE = "PROFESSIONAL_HEADLINE", "Professional headline"
    PROFESSIONAL_SUMMARY = "PROFESSIONAL_SUMMARY", "Professional summary"
    PRIMARY_ROLE = "PRIMARY_ROLE", "Primary role"
    ADDITIONAL_ROLES = "ADDITIONAL_ROLES", "Additional roles"
    INDUSTRIES_SERVED = "INDUSTRIES_SERVED", "Industries served"
    PROJECT_RESPONSIBILITY_BULLETS = (
        "PROJECT_RESPONSIBILITY_BULLETS",
        "Project responsibility bullets",
    )
    TOTAL_CAREER_EXPERIENCE = "TOTAL_CAREER_EXPERIENCE", "Total career experience"
    DEPLOYABILITY_FLAG = "DEPLOYABILITY_FLAG", "Deployability flag"
    CREDENTIAL_STATUS = "CREDENTIAL_STATUS", "Credential status"
    CANDIDATE_MENTOR_CLASSIFICATION = (
        "CANDIDATE_MENTOR_CLASSIFICATION",
        "Candidate/Mentor classification",
    )


class Calculated2FieldCode(models.TextChoices):
    """Controlled catalog of the 15 system-calculated fields. Keeps
    reporting/policy lookups (e.g. "requires four-eyes approval")
    independent of the free-text field_name on the target model.
    """    
    QUALION_LEVEL = "QUALION_LEVEL", "Qualion level (L0-L5)"   
    DEPLOYABILITY_FLAG = "DEPLOYABILITY_FLAG", "Deployability flag"   
    CANDIDATE_MENTOR_CLASSIFICATION = (
        "CANDIDATE_MENTOR_CLASSIFICATION",
        "Candidate/Mentor classification",
    )

class CalculatedFieldOverride(UUIDModel, TenantOwnedModel, CreatedOnlyModel):
    """One override/correction request against a system-calculated field,
    carried through recommendation and final decision.

    Key rules: system_calculated_value is a snapshot and is never edited
    after creation. requested_by can never equal approved_by. reviewed_by
    (recommendation) and approved_by (final decision) are always
    distinguishable, even when the same person is technically eligible
    for both roles on a low-risk field. Approved records are immutable;
    a later correction creates a new row referencing this one via
    supersedes, preserving the full chain.
    """

    class RequestType(models.TextChoices):
        CORRECTION = "CORRECTION", "Correction"
        EXCEPTIONAL_OVERRIDE = "EXCEPTIONAL_OVERRIDE", "Exceptional override"

    class Decision(models.TextChoices):
        PENDING = "PENDING", "Pending"
        UNDER_REVIEW = "UNDER_REVIEW", "Under review"
        RECOMMENDED = "RECOMMENDED", "Recommended"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        WITHDRAWN = "WITHDRAWN", "Withdrawn"
        EXPIRED = "EXPIRED", "Expired"

    class OverrideReasonCode(models.TextChoices):
        SOURCE_DATA_INCORRECT = "SOURCE_DATA_INCORRECT", "Source data incorrect"
        SOURCE_DATA_INCOMPLETE = "SOURCE_DATA_INCOMPLETE", "Source data incomplete"
        RULE_DOES_NOT_FIT_SITUATION = (
            "RULE_DOES_NOT_FIT_SITUATION",
            "Automated rule does not represent the professional situation",
        )
        EVIDENCE_RECEIVED_LATE = "EVIDENCE_RECEIVED_LATE", "Additional evidence received after calculation"
        SYSTEM_DEFECT = "SYSTEM_DEFECT", "System/calculation defect"
        OTHER = "OTHER", "Other (see rationale)"

    # --- target being overridden -----------------------------------
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name="calculated_field_overrides",
        help_text="Target model holding the calculated field (e.g. "
        "competency.ProfessionalScope, professionals.ProfessionalProfile, "
        "professionals.CredentialRecord).",
    )
    object_id = models.PositiveBigIntegerField(help_text="Target row identifier.")
    target = GenericForeignKey("content_type", "object_id")
    field_name = models.CharField(
        max_length=80,
        help_text="Exact field name on the target model holding the "
        "current deciding value, e.g. 'current_qualion_level', "
        "'is_deployable', 'headline'.",
    )
    calculation_field_code = models.CharField(
        max_length=40,
        choices=CalculatedFieldCode.choices,
        db_index=True,
        help_text="Which of the 15 system-calculated fields this is, "
        "independent of the target model/field_name.",
    )

    # --- professional context (denormalised for fast queries) -------
    professional = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.CASCADE,
        related_name="calculated_field_overrides",
        db_index=True,
        help_text="Professional the calculated field belongs to.",
    )

    # --- the request -------------------------------------------------
    request_type = models.CharField(
        max_length=30,
        choices=RequestType.choices,
        help_text="Correction (source data was wrong) or Exceptional "
        "Override (source data is right, rule doesn't fit).",
    )
    system_calculated_value = models.JSONField(
        help_text="Original system output at the time of the request. "
        "Immutable snapshot; never overwritten even after approval.",
    )
    system_calculated_at = models.DateTimeField(
        help_text="When the system produced system_calculated_value."
    )
    system_ruleset_version = models.CharField(
        max_length=30, blank=True, help_text="Calculation ruleset/version used."
    )
    proposed_value = models.JSONField(
        help_text="Value the requester/reviewer is proposing instead."
    )
    override_reason_code = models.CharField(
        max_length=40,
        choices=OverrideReasonCode.choices,
        help_text="Controlled reason category for the proposed change.",
    )
    rationale = models.TextField(
        max_length=3000,
        help_text="Detailed justification for the proposed value. Always required.",
    )
    evidence = models.ForeignKey(
        "evidence.EvidenceDocument",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="calculated_field_overrides",
        help_text="Supporting evidence/document reference. Required for "
        "EXCEPTIONAL_OVERRIDE; recommended for CORRECTION.",
    )
    requested_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        related_name="calculated_field_overrides_requested",
        help_text="User who raised the request; may be the professional "
        "themselves (request only, never self-approve) or a reviewer.",
    )
    requested_at = models.DateTimeField(help_text="Request submission timestamp.")

    # --- reviewer recommendation (mentor / technical reviewer) -------
    reviewed_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="calculated_field_overrides_reviewed",
        help_text="Mentor/technical reviewer who assessed the request; "
        "cannot equal requested_by for reviewer-required fields; cannot "
        "equal the professional.",
    )
    review_notes = models.TextField(
        max_length=3000, blank=True, help_text="Reviewer's assessment notes."
    )
    reviewed_at = models.DateTimeField(
        null=True, blank=True, help_text="Required once decision leaves PENDING."
    )

    # --- final decision (authorised decision-maker / validator) ------
    decision = models.CharField(
        max_length=20,
        choices=Decision.choices,
        default=Decision.PENDING,
        db_index=True,
        help_text="Current workflow state of this override request.",
    )
    final_approved_value = models.JSONField(
        null=True,
        blank=True,
        help_text="Value confirmed by the approver; required when decision=APPROVED. "
        "This becomes the new current deciding value on the target field "
        "and is also written to CalculatedFieldValueHistory.",
    )
    approved_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="calculated_field_overrides_approved",
        help_text="Authorised Competency Decision-Maker/Validator; cannot "
        "equal requested_by; cannot equal the professional; separation of "
        "duties enforced at the service layer per role/permission, not "
        "merely administrative access.",
    )
    decision_reason = models.TextField(
        max_length=3000,
        blank=True,
        help_text="Required for REJECTED; recommended for all non-PENDING decisions.",
    )
    approved_at = models.DateTimeField(
        null=True, blank=True, help_text="Required when decision is APPROVED or REJECTED."
    )
    four_eyes_required = models.BooleanField(
        default=False,
        help_text="Set true for L4/L5 and other high-impact outcomes per "
        "QUALION_QP-10; reviewed_by and approved_by must then be different "
        "authorised individuals.",
    )

    # --- effective window ---------------------------------------------
    effective_from = models.DateField(
        null=True, blank=True, help_text="Date the final_approved_value takes effect."
    )
    review_due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Optional re-review/expiry date, mainly for time-bound "
        "EXCEPTIONAL_OVERRIDE decisions.",
    )

    # --- version chain --------------------------------------------------
    supersedes = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="superseded_by",
        help_text="Prior override request for the same target+field that "
        "this one replaces or re-opens, preserving full request history.",
    )

    class Meta:
        db_table = "governance_calculated_field_override"
        verbose_name = "CalculatedFieldOverride"
        verbose_name_plural = "CalculatedFieldOverride"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id", "field_name"]),
            models.Index(fields=["professional", "calculation_field_code"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=~Q(requested_by=F("approved_by")),
                name="chk_calc_override_requester_not_approver",
            ),
            models.CheckConstraint(
                check=(~Q(decision="APPROVED") | Q(final_approved_value__isnull=False)),
                name="chk_calc_override_final_value_required_on_approval",
            ),
            models.CheckConstraint(
                check=(~Q(decision="APPROVED") | Q(approved_by__isnull=False)),
                name="chk_calc_override_approver_required_on_approval",
            ),
            models.CheckConstraint(
                check=(~Q(decision="REJECTED") | ~Q(decision_reason="")),
                name="chk_calc_override_decision_reason_required_on_rejection",
            ),
            models.CheckConstraint(
                check=(~Q(decision__in=["APPROVED", "REJECTED"]) | Q(approved_at__isnull=False)),
                name="chk_calc_override_approved_at_required",
            ),
            models.CheckConstraint(
                check=(~Q(request_type="EXCEPTIONAL_OVERRIDE") | Q(evidence__isnull=False)),
                name="chk_calc_override_evidence_required_for_exception",
            ),
        ]

    def __str__(self):
        return f"{self.professional} — {self.calculation_field_code} ({self.decision})"


class CalculatedFieldValueHistory(TenantOwnedModel, CreatedOnlyModel):
    """Append-only ledger of every change to the CURRENT deciding value
    of a system-calculated field, regardless of whether the change came
    from a routine system recalculation or an approved override.

    Key rules: Never updated or deleted after creation. One row per
    change. Reconstructing "what was this value as of date X" is a
    simple query against this table; the main/related table (e.g.
    ProfessionalScope) always holds only the latest/current value.
    """

    class ChangeSource(models.TextChoices):
        SYSTEM_RECALCULATION = "SYSTEM_RECALCULATION", "System recalculation"
        CORRECTION_RECALCULATION = (
            "CORRECTION_RECALCULATION",
            "Recalculated after source-record correction",
        )
        OVERRIDE_APPROVED = "OVERRIDE_APPROVED", "Exceptional override approved"

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name="calculated_field_value_history",
        help_text="Target model holding the calculated field.",
    )
    object_id = models.PositiveBigIntegerField(help_text="Target row identifier.")
    target = GenericForeignKey("content_type", "object_id")
    field_name = models.CharField(
        max_length=80, help_text="Exact field name on the target model."
    )
    calculation_field_code = models.CharField(
        max_length=40,
        choices=CalculatedFieldCode.choices,
        db_index=True,
        help_text="Which of the 15 system-calculated fields this change belongs to.",
    )
    professional = models.ForeignKey(
        "professionals.ProfessionalProfile",
        on_delete=models.CASCADE,
        related_name="calculated_field_value_history",
        db_index=True,
        help_text="Professional the calculated field belongs to.",
    )
    previous_value = models.JSONField(
        null=True, blank=True, help_text="Value immediately before this change; NULL for the first record."
    )
    new_value = models.JSONField(help_text="Value immediately after this change (the new current value).")
    change_source = models.CharField(
        max_length=30,
        choices=ChangeSource.choices,
        db_index=True,
        help_text="Why the value changed.",
    )
    override = models.ForeignKey(
        CalculatedFieldOverride,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="value_history_entries",
        help_text="Required when change_source=OVERRIDE_APPROVED; links "
        "the value change back to its full request/approval trail.",
    )
    changed_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calculated_field_value_changes",
        help_text="NULL for system-triggered recalculations; set for "
        "override-driven changes (normally the approver).",
    )
    effective_from = models.DateField(
        null=True, blank=True, help_text="Date the new_value takes/took effect."
    )
    recalculation_ruleset_version = models.CharField(
        max_length=30,
        blank=True,
        help_text="Ruleset/version used, for SYSTEM_RECALCULATION/CORRECTION_RECALCULATION rows.",
    )

    class Meta:
        db_table = "governance_calculated_field_value_history"
        verbose_name = "CalculatedFieldValueHistory"
        verbose_name_plural = "CalculatedFieldValueHistory"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id", "field_name", "-created_at"]),
            models.Index(fields=["professional", "calculation_field_code", "-created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=(~Q(change_source="OVERRIDE_APPROVED") | Q(override__isnull=False)),
                name="chk_calc_value_history_override_required",
            ),
        ]

    def __str__(self):
        return f"{self.professional} — {self.calculation_field_code} @ {self.created_at}"
    



class CalculationRuleSet(UUIDModel, TenantOwnedModel, TimeStampedModel):
    """One versioned, tenant-authored ruleset for deriving a single
    system-calculated field, optionally scoped to one Industry/Scope.

    Key rules: Unique tenant + calculation_field_code + scope + version.
    Only one version may be PUBLISHED at a time for the same
    tenant+field+scope; publishing supersedes and retires the previous
    PUBLISHED version automatically at the service layer. Published
    rule sets and their rules are immutable; edits require a new
    version via `supersedes`.
    """

    calculation_field_code = models.CharField(
        max_length=40,
        choices=CalculatedFieldCode.choices,
        db_index=True,
        help_text="Which of the 15 system-calculated fields this rule "
        "set derives.",
    )
    scope = models.ForeignKey(
        "catalog.ScopeCatalog",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="calculation_rule_sets",
        help_text="Industry/Scope this rule set applies to. NULL means "
        "tenant-wide default, used when no scope-specific PUBLISHED "
        "rule set exists. Required in practice for QUALION_LEVEL and "
        "HIGHEST_AUTHORITY_REACHED, which must not be evaluated globally.",
    )
    version = models.CharField(
        max_length=30, help_text="Rule set version label, e.g. '2026.1'."
    )
    title = models.CharField(
        max_length=180, help_text="Short admin-facing name for this rule set."
    )
    description = models.TextField(
        max_length=2000, blank=True, help_text="Purpose and summary of this rule set."
    )
    status = models.CharField(
        max_length=20,
        choices=PublicationStatus.choices,
        default=PublicationStatus.DRAFT,
        db_index=True,
        help_text="Publication status. Only PUBLISHED rule sets are used "
        "by the calculation engine.",
    )
    default_requires_human_confirmation = models.BooleanField(
        default=True,
        help_text="Whether concluded values from this rule set are treated "
        "as a System Recommendation requiring human confirmation before "
        "becoming a Final value (per QP-14), unless an individual rule "
        "overrides this with requires_four_eyes_approval/skip_confirmation.",
    )
    effective_from = models.DateField(
        null=True, blank=True, help_text="Date this rule set becomes effective once published."
    )
    effective_to = models.DateField(
        null=True, blank=True, help_text="Date this rule set stops being used, if scheduled for retirement."
    )
    created_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        related_name="calculation_rule_sets_created",
        help_text="Tenant Admin/authorised author who created this rule set.",
    )
    published_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="calculation_rule_sets_published",
        help_text="User who published this version; required when PUBLISHED.",
    )
    published_at = models.DateTimeField(
        null=True, blank=True, help_text="Required when status=PUBLISHED."
    )
    retired_at = models.DateTimeField(
        null=True, blank=True, help_text="Required when status=RETIRED."
    )
    supersedes = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="superseded_by",
        help_text="Prior version of this tenant+field(+scope) rule set "
        "that this version replaces.",
    )

    class Meta:
        db_table = "governance_calculation_rule_set"
        verbose_name = "CalculationRuleSet"
        verbose_name_plural = "CalculationRuleSet"
        ordering = ["calculation_field_code", "scope", "-version"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "calculation_field_code", "scope", "version"],
                name="uniq_calc_rule_set_tenant_field_scope_version",
            ),
            models.CheckConstraint(
                check=(~Q(status="PUBLISHED") | Q(published_at__isnull=False)),
                name="chk_calc_rule_set_published_at_required",
            ),
            models.CheckConstraint(
                check=(~Q(status="PUBLISHED") | Q(published_by__isnull=False)),
                name="chk_calc_rule_set_published_by_required",
            ),
            models.CheckConstraint(
                check=(~Q(status="RETIRED") | Q(retired_at__isnull=False)),
                name="chk_calc_rule_set_retired_at_required",
            ),
        ]

    def clean(self):
        super().clean()
        if self.supersedes_id and self.supersedes_id == self.id:
            raise ValidationError({"supersedes": "Rule set cannot supersede itself."})

    def __str__(self):
        scope_label = self.scope or "tenant-wide"
        return f"{self.tenant} — {self.calculation_field_code} — {scope_label} v{self.version} ({self.status})"


# class CalculationRule(TenantOwnedModel, TimeStampedModel):
#     """One threshold rule row within a CalculationRuleSet: fixed, typed
#     condition columns plus the value the system concludes when they are
#     met — no free-form JSON.

#     Scope variation is handled entirely by the parent CalculationRuleSet
#     (CalculationRuleSet.scope): a rule set is already unique per
#     tenant+calculation_field_code+scope+version, so every rule under a
#     scope-specific rule set only ever gets evaluated for that one
#     Industry/Scope. Nothing here needs its own scope column.

#     Every condition column is nullable and independent: leave one NULL/
#     blank to exclude it from this rule entirely, rather than needing a
#     JSON key present or absent. Only the columns relevant to the parent
#     rule_set.calculation_field_code are expected to be populated — the
#     rest stay empty and are simply ignored by the engine. Exactly one of
#     the three concluded_* columns should be populated, matching that same
#     calculation_field_code; clean() enforces this.

#     Key rule: evaluated in `sequence` order within its rule set; the
#     first rule whose populated conditions are satisfied by the
#     professional's actual parameters (per match_type) wins.
#     """

#     class MatchType(models.TextChoices):
#         ALL_CONDITIONS = "ALL_CONDITIONS", "All conditions must be met"
#         ANY_CONDITION = "ANY_CONDITION", "Any one condition is sufficient"

#     class AssessmentDecision(models.TextChoices):
#         """Mirrors competency.CompetencyAssessment.Decision — duplicated
#         rather than imported cross-app to avoid coupling governance to
#         competency; keep these two in sync if either changes."""

#         DRAFT = "DRAFT", "Draft"
#         SUBMITTED = "SUBMITTED", "Submitted"
#         APPROVED = "APPROVED", "Approved"
#         REJECTED = "REJECTED", "Rejected"

#     class DeployabilityStatus(models.TextChoices):
#         """Mirrors competency.ProfessionalScope.DeployabilityStatus —
#         duplicated rather than imported cross-app; keep in sync."""

#         DEPLOYABLE = "DEPLOYABLE", "Deployable"
#         DEPLOYABLE_WITH_RESTRICTIONS = "DEPLOYABLE_WITH_RESTRICTIONS", "Deployable with restrictions"
#         REVIEW_REQUIRED = "REVIEW_REQUIRED", "Review required"
#         NOT_DEPLOYABLE = "NOT_DEPLOYABLE", "Not deployable"

#     class Classification(models.TextChoices):
#         """Mirrors professionals.ProfessionalReview's classification
#         values. BOTH is a valid system recommendation here, but
#         ProfessionalReview.final_classification only ever accepts
#         CANDIDATE or MENTOR once a human confirms — see the classification
#         engine notes elsewhere in this codebase."""

#         CANDIDATE = "CANDIDATE", "Candidate"
#         MENTOR = "MENTOR", "Mentor"
#         BOTH = "BOTH", "Both"
#         UNCLASSIFIED = "UNCLASSIFIED", "Unclassified"

#     rule_set = models.ForeignKey(
#         CalculationRuleSet,
#         on_delete=models.CASCADE,
#         related_name="rules",
#         db_index=True,
#         help_text="Owning rule set. Must equal rule_set.tenant. Scope and "
#         "calculation_field_code both come from here, not repeated here.",
#     )
#     sequence = models.PositiveSmallIntegerField(
#         help_text="Evaluation order within the rule set; lower runs first. "
#         "First matching rule wins."
#     )
#     label = models.CharField(
#         max_length=160,
#         help_text="Admin-facing description, e.g. 'Level 4 — Independent authority'.",
#     )
#     match_type = models.CharField(
#         max_length=20,
#         choices=MatchType.choices,
#         default=MatchType.ALL_CONDITIONS,
#         help_text="Whether every populated condition, or any single one, "
#         "triggers this rule.",
#     )

#     # ------------------------------------------------------------------
#     # Conditions — fixed, typed thresholds instead of a JSON blob.
#     # ------------------------------------------------------------------
#     min_calendar_experience_months = models.PositiveIntegerField(
#         null=True,
#         blank=True,
#         help_text="Minimum ProfessionalScope.calendar_experience_months "
#         "for this scope.",
#     )
#     min_verified_field_days = models.DecimalField(
#         max_digits=8,
#         decimal_places=2,
#         null=True,
#         blank=True,
#         help_text="Minimum ProfessionalScope.verified_field_days for this scope.",
#     )
#     min_verified_project_count = models.PositiveIntegerField(
#         null=True,
#         blank=True,
#         help_text="Minimum ProfessionalScope.verified_project_count "
#         "(approved/verified projects) for this scope.",
#     )
#     min_qualion_level = models.ForeignKey(
#         "catalog.ReferenceValue",
#         on_delete=models.PROTECT,
#         null=True,
#         blank=True,
#         related_name="calc_rules_min_qualion_level",
#         help_text="Minimum current_qualion_level rank required, ranked by "
#         "ReferenceValue.sort_order (option_set QUALION_LEVEL). Used by "
#         "DEPLOYABILITY_FLAG/CANDIDATE_MENTOR_CLASSIFICATION rules — not "
#         "QUALION_LEVEL rules themselves, which would be circular.",
#     )
#     min_authority_status = models.ForeignKey(
#         "catalog.ReferenceValue",
#         on_delete=models.PROTECT,
#         null=True,
#         blank=True,
#         related_name="calc_rules_min_authority_status",
#         help_text="Minimum current_authority_status rank required, ranked "
#         "by sort_order (option_set AUTHORITY_STATUS).",
#     )
#     min_complexity_rating = models.ForeignKey(
#         "catalog.ReferenceValue",
#         on_delete=models.PROTECT,
#         null=True,
#         blank=True,
#         related_name="calc_rules_min_complexity_rating",
#         help_text="Minimum complexity_rating rank required, ranked by "
#         "sort_order (option_set COMPLEXITY).",
#     )
#     min_ethics_independence_score = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         null=True,
#         blank=True,
#         help_text="Minimum latest CompetencyAssessment."
#         "ethics_independence_score (0.00-100.00). "
#         "CANDIDATE_MENTOR_CLASSIFICATION rules only.",
#     )
#     require_latest_assessment_decision = models.CharField(
#         max_length=20,
#         blank=True,
#         choices=AssessmentDecision.choices,
#         help_text="The latest CompetencyAssessment for this professional+"
#         "scope must have this decision (e.g. APPROVED) for the rule to "
#         "match. Blank = not checked.",
#     )
#     required_credential_types = models.ManyToManyField(
#         "catalog.ReferenceValue",
#         blank=True,
#         related_name="calc_rules_requiring_credential",
#         help_text="Professional must hold a CredentialRecord of at least "
#         "one of these types (option_set CREDENTIAL_TYPE) for this scope. "
#         "Empty = no credential required by this rule.",
#     )
#     require_active_credential = models.BooleanField(
#         default=False,
#         help_text="Only meaningful when required_credential_types is set: "
#         "whether the matching credential must currently be status=ACTIVE, "
#         "vs. any status.",
#     )
#     max_days_to_credential_expiry = models.PositiveSmallIntegerField(
#         null=True,
#         blank=True,
#         help_text="Only meaningful when required_credential_types is set: "
#         "the matching credential must expire within this many days "
#         "(e.g. 30) — used for 'expiring soon' deployability rules. Leave "
#         "blank to not check expiry at all.",
#     )
#     block_if_pending_rejection = models.BooleanField(
#         default=False,
#         help_text="If true, this rule does not match while the professional "
#         "has an unresolved REJECTED ProfessionalReview of type "
#         "RECLASSIFICATION. CANDIDATE_MENTOR_CLASSIFICATION rules only.",
#     )

#     # ------------------------------------------------------------------
#     # Concluded value — exactly one populated, matching
#     # rule_set.calculation_field_code; enforced in clean().
#     # ------------------------------------------------------------------
#     concluded_qualion_level = models.ForeignKey(
#         "catalog.ReferenceValue",
#         on_delete=models.PROTECT,
#         null=True,
#         blank=True,
#         related_name="calc_rules_concluded_qualion_level",
#         help_text="Value assigned when this rule matches. QUALION_LEVEL "
#         "rule sets only (option_set QUALION_LEVEL).",
#     )
#     concluded_deployability_status = models.CharField(
#         max_length=30,
#         blank=True,
#         choices=DeployabilityStatus.choices,
#         help_text="Value assigned when this rule matches. DEPLOYABILITY_FLAG "
#         "rule sets only.",
#     )
#     concluded_classification = models.CharField(
#         max_length=20,
#         blank=True,
#         choices=Classification.choices,
#         help_text="Value assigned when this rule matches. "
#         "CANDIDATE_MENTOR_CLASSIFICATION rule sets only.",
#     )

#     requires_four_eyes_approval = models.BooleanField(
#         default=False,
#         help_text="Overrides rule_set.default_requires_human_confirmation for "
#         "this specific concluded value; set true for L4/L5 and other "
#         "high-impact outcomes per QUALION_QP-10, requiring reviewer and "
#         "approver to be different authorised individuals.",
#     )
#     is_active = models.BooleanField(
#         default=True,
#         help_text="Allows disabling a single rule without creating a new rule set version, "
#         "only while the rule set itself is still DRAFT.",
#     )

#     class Meta:
#         db_table = "governance_calculation_rule"
#         verbose_name = "CalculationRule"
#         verbose_name_plural = "CalculationRule"
#         ordering = ["rule_set", "sequence"]
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["rule_set", "sequence"],
#                 name="uniq_calc_rule_rule_set_sequence",
#             ),
#         ]

#     def clean(self):
#         super().clean()
#         if self.rule_set_id and self.tenant_id and self.rule_set.tenant_id != self.tenant_id:
#             raise ValidationError({"rule_set": "rule_set.tenant must match this rule's tenant."})

#         if not self.rule_set_id:
#             return
#         field_code = self.rule_set.calculation_field_code
#         concluded_field_for_code = {
#             CalculatedFieldCode.QUALION_LEVEL: "concluded_qualion_level_id",
#             CalculatedFieldCode.DEPLOYABILITY_FLAG: "concluded_deployability_status",
#             CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION: "concluded_classification",
#         }
#         expected_field = concluded_field_for_code.get(field_code)
#         if expected_field is None:
#             raise ValidationError({
#                 "rule_set": f"{field_code} is not one of the 3 rule-driven "
#                 "fields (QUALION_LEVEL, DEPLOYABILITY_FLAG, "
#                 "CANDIDATE_MENTOR_CLASSIFICATION) — it should never have a "
#                 "CalculationRule at all; it's a fixed formula."
#             })
#         if not getattr(self, expected_field):
#             raise ValidationError({
#                 expected_field: f"Required for a {field_code} rule."
#             })
#         for other_field in concluded_field_for_code.values():
#             if other_field != expected_field and getattr(self, other_field):
#                 raise ValidationError({
#                     other_field: f"Not applicable to a {field_code} rule "
#                     f"— only {expected_field} should be set."
#                 })

#     def __str__(self):
#         return f"{self.rule_set} — #{self.sequence} {self.label}"


class CalculationRule(TenantOwnedModel, TimeStampedModel):
    """One threshold rule for one of the 3 genuinely rule-driven system-
    calculated fields (QUALION_LEVEL, DEPLOYABILITY_FLAG,
    CANDIDATE_MENTOR_CLASSIFICATION) — fixed, typed condition columns
    plus the concluded value, with calculation_field_code and scope
    directly on the row instead of via a CalculationRuleSet wrapper.

    Trade-off accepted by collapsing CalculationRuleSet into this table:
    there is no DRAFT/PUBLISHED staging, no version number, and no
    supersedes chain — editing a rule (or its is_active flag) takes
    effect immediately, and once changed there's no record of what the
    row looked like before. If you need to stage a threshold change for
    review before it goes live, or need to answer "what was L3's
    threshold last quarter," that requires CalculationRuleSet back.

    Key rule: for one tenant+calculation_field_code+scope combination,
    rules are evaluated in `sequence` order; the first rule whose
    populated conditions are satisfied by the professional's actual
    parameters (per match_type) wins.
    """

    class MatchType(models.TextChoices):
        ALL_CONDITIONS = "ALL_CONDITIONS", "All conditions must be met"
        ANY_CONDITION = "ANY_CONDITION", "Any one condition is sufficient"

    class AssessmentDecision(models.TextChoices):
        """Mirrors competency.CompetencyAssessment.Decision — duplicated
        rather than imported cross-app; keep in sync if either changes."""

        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    class DeployabilityStatus(models.TextChoices):
        """Mirrors competency.ProfessionalScope.DeployabilityStatus —
        duplicated rather than imported cross-app; keep in sync."""

        DEPLOYABLE = "DEPLOYABLE", "Deployable"
        DEPLOYABLE_WITH_RESTRICTIONS = "DEPLOYABLE_WITH_RESTRICTIONS", "Deployable with restrictions"
        REVIEW_REQUIRED = "REVIEW_REQUIRED", "Review required"
        NOT_DEPLOYABLE = "NOT_DEPLOYABLE", "Not deployable"

    class Classification(models.TextChoices):
        """BOTH is a valid system recommendation here, but
        ProfessionalReview.final_classification only ever accepts
        CANDIDATE or MENTOR once a human confirms."""

        CANDIDATE = "CANDIDATE", "Candidate"
        MENTOR = "MENTOR", "Mentor"
        BOTH = "BOTH", "Both"
        UNCLASSIFIED = "UNCLASSIFIED", "Unclassified"

    # The only 3 valid values — enforced in clean(), see below.
    calculation_field_choices = [
        ('QUALION_LEVEL', 'QUALION_LEVEL'),
        ('DEPLOYABILITY_FLAG', 'DEPLOYABILITY_FLAG'),
        ('CANDIDATE_MENTOR_CLASSIFICATION', 'CANDIDATE_MENTOR_CLASSIFICATION'),
    ]

    calculation_field_code = models.CharField(
        max_length=40,
        choices=calculation_field_choices,
        db_index=True,
        null=True, blank=True,
        help_text="Which system-calculated field this rule belongs to. "
        "Only QUALION_LEVEL, DEPLOYABILITY_FLAG and "
        "CANDIDATE_MENTOR_CLASSIFICATION are valid here — the other 12 "
        "fields are fixed formulas and never have a CalculationRule; "
        "enforced in clean().",
    )
    scope = models.ManyToManyField(
        "catalog.ScopeCatalog",
        blank=True,
        related_name="calculation_rules",
        help_text=(
            "Industry/Scopes this rule applies to. "
            "An empty selection means tenant-wide "
            "(e.g. CANDIDATE_MENTOR_CLASSIFICATION is typically evaluated "
            "across a professional's best scope, not one specific scope). "
            "At least one scope is expected for QUALION_LEVEL and "
            "DEPLOYABILITY_FLAG."
        ),
    )
    sequence = models.PositiveSmallIntegerField(
        help_text="Evaluation order within this tenant+field+scope ladder; "
        "lower runs first. First matching rule wins."
    )
    label = models.CharField(
        max_length=160,
        help_text="Admin-facing description, e.g. 'Level 4 — Independent authority'.",
    )
    match_type = models.CharField(
        max_length=20,
        choices=MatchType.choices,
        default=MatchType.ALL_CONDITIONS,
        help_text="Whether every populated condition, or any single one, "
        "triggers this rule.",
    )

    # ------------------------------------------------------------------
    # Conditions — fixed, typed thresholds instead of a JSON blob. Each
    # is nullable/independent: leave one blank to exclude it from this
    # rule entirely.
    # ------------------------------------------------------------------
    #QUALION_LEVEL field
    min_calendar_experience_months = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Minimum ProfessionalScope.calendar_experience_months "
        "for this scope.",
    )
    max_calendar_experience_months = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum ProfessionalScope.calendar_experience_months "
        "for this scope.",
    )
    #QUALION_LEVEL field
    min_verified_field_days = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum ProfessionalScope.verified_field_days for this scope.",
    )
    max_verified_field_days = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum ProfessionalScope.verified_field_days for this scope.",
    )
    #QUALION_LEVEL field
    min_verified_project_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Minimum ProfessionalScope.verified_project_count "
        "(approved/verified projects) for this scope.",
    )
    max_verified_project_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum ProfessionalScope.verified_project_count "
        "(approved/verified projects) for this scope.",
    )
    #DEPLOYABILITY_FLAG and CANDIDATE_MENTOR_CLASSIFICATION fields
    min_qualion_level = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="calc_rules_min_qualion_level",
        help_text="Minimum current_qualion_level rank required, ranked by "
        "ReferenceValue.sort_order (option_set QUALION_LEVEL). Used by "
        "DEPLOYABILITY_FLAG/CANDIDATE_MENTOR_CLASSIFICATION rules — not "
        "QUALION_LEVEL rules themselves, which would be circular.",
    )
    max_qualion_level = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="calc_rules_max_qualion_level",
        help_text="Maximum current_qualion_level rank required, ranked by "
        "ReferenceValue.sort_order (option_set QUALION_LEVEL). Used by "
        "DEPLOYABILITY_FLAG/CANDIDATE_MENTOR_CLASSIFICATION rules — not "
        "QUALION_LEVEL rules themselves, which would be circular.",
    )
    #All 3 fields
    min_authority_status = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="calc_rules_min_authority_status",
        help_text="Minimum current_authority_status rank required, ranked "
        "by sort_order (option_set AUTHORITY_STATUS).",
    )
    #QUALION_LEVEL field
    min_complexity_rating = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="calc_rules_min_complexity_rating",
        help_text="Minimum complexity_rating rank required, ranked by "
        "sort_order (option_set COMPLEXITY).",
    )
    #CANDIDATE_MENTOR_CLASSIFICATION field
    min_ethics_independence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum latest CompetencyAssessment."
        "ethics_independence_score (0.00-100.00). "
        "CANDIDATE_MENTOR_CLASSIFICATION rules only.",
    )
    #CANDIDATE_MENTOR_CLASSIFICATION field
    require_latest_assessment_decision = models.CharField(
        max_length=20,
        blank=True,
        choices=AssessmentDecision.choices,
        help_text="The latest CompetencyAssessment for this professional+"
        "scope must have this decision (e.g. APPROVED) for the rule to "
        "match. Blank = not checked.",
    )
    #QUALION_LEVEL and DEPLOYABILITY_FLAG fields
    required_credential_types = models.ManyToManyField(
        "catalog.ReferenceValue",
        blank=True,
        related_name="calc_rules_requiring_credential",
        help_text="Professional must hold a CredentialRecord of at least "
        "one of these types (option_set CREDENTIAL_TYPE) for this scope. "
        "Empty = no credential required by this rule.",
    )
    #QUALION_LEVEL and DEPLOYABILITY_FLAG fields
    require_active_credential = models.BooleanField(
        default=False,
        help_text="Only meaningful when required_credential_types is set: "
        "whether the matching credential must currently be status=ACTIVE, "
        "vs. any status.",
    )
    #DEPLOYABILITY_FLAG 
    max_days_to_credential_expiry = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Only meaningful when required_credential_types is set: "
        "the matching credential must expire within this many days "
        "(e.g. 30) — used for 'expiring soon' deployability rules. Leave "
        "blank to not check expiry at all.",
    )
    #CANDIDATE_MENTOR_CLASSIFICATION field
    block_if_pending_rejection = models.BooleanField(
        default=False,
        help_text="If true, this rule does not match while the professional "
        "has an unresolved REJECTED ProfessionalReview of type "
        "RECLASSIFICATION. CANDIDATE_MENTOR_CLASSIFICATION rules only.",
    )

    # ------------------------------------------------------------------
    # Concluded value — exactly one populated, matching
    # calculation_field_code; enforced in clean().
    # ------------------------------------------------------------------
    #QUALION_LEVEL field
    concluded_qualion_level = models.ForeignKey(
        "catalog.ReferenceValue",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="calc_rules_concluded_qualion_level",
        help_text="Value assigned when this rule matches. QUALION_LEVEL "
        "rules only (option_set QUALION_LEVEL).",
    )
    #DEPLOYABILITY_FLAG field
    concluded_deployability_status = models.CharField(
        max_length=30,
        blank=True,
        choices=DeployabilityStatus.choices,
        help_text="Value assigned when this rule matches. DEPLOYABILITY_FLAG "
        "rules only.",
    )
    #CANDIDATE_MENTOR_CLASSIFICATION field
    concluded_classification = models.CharField(
        max_length=20,
        blank=True,
        choices=Classification.choices,
        help_text="Value assigned when this rule matches. "
        "CANDIDATE_MENTOR_CLASSIFICATION rules only.",
    )
    #All 3 fields: overrides rule_set.default_requires_human_confirmation for this specific concluded value; set true for L4/L5 and other high-impact outcomes per QUALION_QP-10, requiring reviewer and approver to be different authorised individuals.
    requires_four_eyes_approval = models.BooleanField(
        default=False,
        help_text="Set true for L4/L5 and other high-impact outcomes per "
        "QUALION_QP-10, requiring reviewer and approver to be different "
        "authorised individuals.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Disable a single rule without deleting it. Takes effect "
        "immediately — there is no DRAFT/PUBLISHED staging here.",
    )
    created_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT, null=True, blank=True,
        related_name="calculation_rules_created",
        help_text="Tenant Admin/authorised author who created this rule.",
    )

    class Meta:
        db_table = "governance_calculation_rule"
        verbose_name = "CalculationRule"
        verbose_name_plural = "CalculationRule"
        ordering = ["calculation_field_code", "sequence"]

    def clean(self):
        super().clean()
        if self.calculation_field_code not in self.RULE_DRIVEN_FIELD_CODES:
            raise ValidationError({
                "calculation_field_code": f"{self.calculation_field_code} is "
                "not one of the 3 rule-driven fields (QUALION_LEVEL, "
                "DEPLOYABILITY_FLAG, CANDIDATE_MENTOR_CLASSIFICATION) — it's "
                "a fixed formula and should never have a CalculationRule."
            })

        concluded_field_for_code = {
            CalculatedFieldCode.QUALION_LEVEL: "concluded_qualion_level_id",
            CalculatedFieldCode.DEPLOYABILITY_FLAG: "concluded_deployability_status",
            CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION: "concluded_classification",
        }
        expected_field = concluded_field_for_code[self.calculation_field_code]
        if not getattr(self, expected_field):
            raise ValidationError({
                expected_field: f"Required for a {self.calculation_field_code} rule."
            })
        for other_field in concluded_field_for_code.values():
            if other_field != expected_field and getattr(self, other_field):
                raise ValidationError({
                    other_field: f"Not applicable to a {self.calculation_field_code} "
                    f"rule — only {expected_field} should be set."
                })

    def __str__(self):
        if self.pk:
            scopes = self.scope.all()
            scope_label = ", ".join(str(scope) for scope in scopes) or "tenant-wide"
        else:
            scope_label = "tenant-wide"

        return (
            f"{self.tenant} — "
            f"{self.calculation_field_code} — "
            f"{scope_label} — "
            f"#{self.sequence} {self.label}"
        )        




