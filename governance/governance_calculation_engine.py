"""governance/services/calculation_engine.py

The engine behind three endpoints:
  1. POST /api/governance/calculated-fields/calculate/  -> system decides
     ONE of the 3 genuinely rule-driven fields (QUALION_LEVEL,
     DEPLOYABILITY_FLAG, CANDIDATE_MENTOR_CLASSIFICATION) from real data +
     the tenant's PUBLISHED CalculationRuleSet/CalculationRule rows,
     writes it to the main/related table, logs CalculatedFieldValueHistory
     (SYSTEM_RECALCULATION).
  2. POST /api/governance/calculated-fields/override/    -> admin/reviewer
     override, writes CalculatedFieldOverride, and if decision=APPROVED in
     the same call, also writes the field + logs history
     (OVERRIDE_APPROVED).
  3. POST /api/governance/calculated-fields/calculate-fixed/ -> recalculates
     all 12 fixed-formula fields (see FIXED_FIELD_CODES) in one call for a
     professional. These never consult CalculationRuleSet/CalculationRule —
     per the client's own "System Calculated Fields" review sheet, they are
     plain aggregations/templates, not tenant-tunable decisions. Only
     Qualion Level, Deployability Flag and Candidate/Mentor Classification
     are rule-driven; everything else here is a fixed formula keyed off the
     "Based On" column of that sheet.

Project Responsibility Bullets writes into the existing
experience.ProjectRecord.responsibilities field (there's no separate
responsibility_bullets column) and, to protect candidate-entered text,
only ever fills it when it is currently blank.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, models
from django.db.models import Sum
from django.utils import timezone

from catalog.models import ReferenceValue, ScopeCatalog
from competency.models import ProfessionalScope
from competency.models import CompetencyAssessment
from experience.models import EmploymentRecord, ExposureLog, ProjectRecord, ProjectScope
from governance.models import (
    CalculatedFieldCode,
    CalculatedFieldValueHistory,
    CalculationRuleSet,
)
from professionals.models import CredentialRecord, ProfessionalProfile


class CalculationError(Exception):
    """Raised for anything that stops a calculation from being produced or
    applied: missing rule set, missing destination field, bad concluded
    value, etc. Views should turn this into a 400/422 response.
    """


# ---------------------------------------------------------------------
# Which calculation_field_code values are runnable, and on what model
# ---------------------------------------------------------------------

SCOPED_FIELDS = {
    CalculatedFieldCode.CALENDAR_EXPERIENCE,
    CalculatedFieldCode.VERIFIED_FIELD_DAYS,
    CalculatedFieldCode.VERIFIED_PROJECT_COUNT,
    CalculatedFieldCode.HIGHEST_AUTHORITY_REACHED,
    CalculatedFieldCode.QUALION_LEVEL,
    CalculatedFieldCode.DEPLOYABILITY_FLAG,
}
PROFILE_FIELDS = {
    CalculatedFieldCode.PROFESSIONAL_HEADLINE,
    CalculatedFieldCode.PROFESSIONAL_SUMMARY,
    CalculatedFieldCode.PRIMARY_ROLE,
    CalculatedFieldCode.ADDITIONAL_ROLES,
    CalculatedFieldCode.INDUSTRIES_SERVED,
    CalculatedFieldCode.TOTAL_CAREER_EXPERIENCE,
    CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION,
}
SUPPORTED_FIELDS = SCOPED_FIELDS | PROFILE_FIELDS

# The 3 fields that are genuinely tenant-configurable decisions, driven by
# a PUBLISHED CalculationRuleSet/CalculationRule. Everything else in
# SUPPORTED_FIELDS is a fixed formula (see FIXED_FIELD_CODES below).
RULE_DRIVEN_FIELDS = {
    CalculatedFieldCode.QUALION_LEVEL,
    CalculatedFieldCode.DEPLOYABILITY_FLAG,
    CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION,
}

# The fields calculate-fixed recalculates in one call. Fixed formula/
# template per the client's "Based On" column — never reads
# CalculationRuleSet/CalculationRule. Deliberately excludes
# PROJECT_RESPONSIBILITY_BULLETS: no destination field exists on
# ProjectRecord yet, so it's reported SKIPPED rather than guessed.
FIXED_FIELD_CODES = (SUPPORTED_FIELDS - RULE_DRIVEN_FIELDS) | {
    CalculatedFieldCode.CREDENTIAL_STATUS,
    CalculatedFieldCode.PROJECT_RESPONSIBILITY_BULLETS,
}

TARGET_FIELD_NAME = {
    CalculatedFieldCode.CALENDAR_EXPERIENCE: "calendar_experience_months",
    CalculatedFieldCode.VERIFIED_FIELD_DAYS: "verified_field_days",
    CalculatedFieldCode.VERIFIED_PROJECT_COUNT: "verified_project_count",
    CalculatedFieldCode.HIGHEST_AUTHORITY_REACHED: "highest_authority_reached",
    CalculatedFieldCode.QUALION_LEVEL: "current_qualion_level",
    CalculatedFieldCode.DEPLOYABILITY_FLAG: "is_deployable",
    CalculatedFieldCode.PROFESSIONAL_HEADLINE: "headline",
    CalculatedFieldCode.PROFESSIONAL_SUMMARY: "summary",
    CalculatedFieldCode.PRIMARY_ROLE: "primary_role",
    CalculatedFieldCode.ADDITIONAL_ROLES: "additional_roles",
    CalculatedFieldCode.INDUSTRIES_SERVED: "industries_served",
    CalculatedFieldCode.TOTAL_CAREER_EXPERIENCE: "total_career_experience_months",
    CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION: "current_classification",
    # These two are per-record (many rows per professional), applied
    # directly in calculate_fixed_fields_for_professional rather than via
    # FIELD_HANDLERS — listed here for documentation only.
    CalculatedFieldCode.CREDENTIAL_STATUS: "status",
    CalculatedFieldCode.PROJECT_RESPONSIBILITY_BULLETS: "responsibilities",
}

# Which ReferenceValue.option_set a given context key/target field ranks against
OPTION_SET_FOR_KEY = {
    "current_authority_status": "AUTHORITY_STATUS",
    "complexity_rating": "COMPLEXITY",
    "current_qualion_level": "QUALION_LEVEL",
}

VERIFIED_STATES = ["VERIFIED", "VALIDATED"]

# Statuses the client's explicit calculate-fixed spec filters on for every
# one of the 12 fixed fields — SELF_DECLARED/EVIDENCE_UPLOADED/VERIFIED/
# REJECTED, i.e. everything except UNDER_REVIEW/VALIDATED. Deliberately
# separate from VERIFIED_STATES above, which stays VERIFIED/VALIDATED-only
# for the rule-driven fields (Qualion Level, Deployability, Classification)
# that were NOT part of that spec and are untouched here.
FIXED_FIELD_STATUSES = ["SELF_DECLARED", "EVIDENCE_UPLOADED", "VERIFIED", "REJECTED"]


# ---------------------------------------------------------------------
# Aggregation helpers (pure calculation, no rule set involved)
# ---------------------------------------------------------------------

def _merge_date_ranges_to_months(intervals):
    if not intervals:
        return 0
    intervals = sorted(intervals, key=lambda iv: iv[0])
    merged = [list(intervals[0])]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    total_days = sum((end - start).days for start, end in merged)
    return max(0, round(total_days / 30.44))


def _span_in_months(date_pairs):
    """date_pairs: iterable of (start_date, end_date_or_None). Per the
    explicit spec ('order_by start_date ... from start_date of first
    record to end_date of last record'), this is a straight span from
    the earliest start_date to the latest end_date — missing end_date
    (still open) treated as today — NOT a union-merge of overlapping
    intervals like _merge_date_ranges_to_months above."""
    pairs = list(date_pairs)
    if not pairs:
        return 0
    today = timezone.now().date()
    start = min(p[0] for p in pairs)
    end = max((p[1] or today) for p in pairs)
    return max(0, round((end - start).days / 30.44))


def compute_calendar_experience_months(professional, scope):
    """Based On: Project start/end dates linked to that scope. Filters
    ProjectRecord.verification_status against FIXED_FIELD_STATUSES
    (SELF_DECLARED/EVIDENCE_UPLOADED/VERIFIED/REJECTED, per the explicit
    spec — broader than the VERIFIED_STATES used elsewhere in this
    file), joined to this scope via ProjectScope. Span from the earliest
    start_date to the latest end_date (today if still open)."""
    records = (
        ProjectRecord.objects.filter(
            professional=professional,
            project_scopes__scope=scope,
            verification_status__in=FIXED_FIELD_STATUSES,
        )
        .distinct()
        .order_by("start_date")
    )
    return _span_in_months((r.start_date, r.end_date) for r in records)


def compute_verified_field_days(professional, scope):
    """Based On: Field days logged per project, verification status. SUM
    of ProjectRecord.verified_field_days for projects in this scope —
    per the explicit spec this reads the cached per-project field
    directly rather than re-deriving from ExposureLog."""
    total = (
        ProjectRecord.objects.filter(
            professional=professional,
            project_scopes__scope=scope,
            verification_status__in=FIXED_FIELD_STATUSES,
        )
        .distinct()
        .aggregate(total=Sum("verified_field_days"))["total"]
    )
    return total or Decimal("0.00")


def compute_primary_and_additional_roles(professional):
    """Based On: Verified project history per role. Groups every project
    record (all scopes, FIXED_FIELD_STATUSES) by role_title and sums
    each role's project duration in days ('more time taken' per the
    explicit spec) rather than verified_field_days. Primary = the role
    with the largest total; additional = every other distinct
    role_title — no minimum-days floor this time."""
    today = timezone.now().date()
    records = ProjectRecord.objects.filter(
        professional=professional,
        verification_status__in=FIXED_FIELD_STATUSES,
        role_title__isnull=False,
    )
    totals = {}
    for r in records:
        end = r.end_date or today
        days = max(0, (end - r.start_date).days)
        totals[r.role_title_id] = totals.get(r.role_title_id, 0) + days
    if not totals:
        return None, []
    ranked = sorted(totals.items(), key=lambda kv: -kv[1])
    primary_role_id = ranked[0][0]
    additional_role_ids = [role_id for role_id, _ in ranked[1:]]
    return primary_role_id, additional_role_ids


def compute_verified_project_count(professional, scope):
    """Based On: Projects in that scope, verification status. Count of
    ProjectRecord rows in this scope matching FIXED_FIELD_STATUSES."""
    return (
        ProjectRecord.objects.filter(
            professional=professional,
            project_scopes__scope=scope,
            verification_status__in=FIXED_FIELD_STATUSES,
        )
        .distinct()
        .count()
    )


def compute_highest_authority_reached(professional, scope):
    """Based On: Authority level recorded per project, verification
    status. Highest-ranked ProjectScope.authority_action ('Observed'
    through 'Technical Authority') ever recorded for this
    professional+scope — calculated per Industry+Scope, never as one
    global authority (the sheet's explicit correction on this field).
    Filters ProjectScope.verification_status, since authority_action is
    itself a ProjectScope attribute, not a ProjectRecord one.

    NOTE for whoever owns the catalog data: this field's own help_text
    says its option_set must be AUTHORITY_STATUS, but the data it's
    actually sourced from — ProjectScope.authority_action — is
    documented as option_set AUTHORITY_ACTION. Ranking by sort_order
    works regardless of option_set, so this runs fine either way, but
    the two option_sets should be unified or explicitly mapped so the
    ladder is unambiguous."""
    best = (
        ProjectScope.objects.filter(
            project__professional=professional,
            scope=scope,
            verification_status__in=FIXED_FIELD_STATUSES,
            authority_action__isnull=False,
        )
        .select_related("authority_action")
        .order_by("-authority_action__sort_order")
        .first()
    )
    return best.authority_action if best else None


def compute_industries_served(professional):
    """Based On (sheet): Verified scopes and their industries. Per the
    explicit spec, sourced directly from ProjectRecord.industry_classification
    (all scopes, FIXED_FIELD_STATUSES) rather than joined through
    ProfessionalScope -> scope -> industry."""
    codes = (
        ProjectRecord.objects.filter(
            professional=professional,
            verification_status__in=FIXED_FIELD_STATUSES,
            industry_classification__isnull=False,
        )
        .values_list("industry_classification__code", flat=True)
        .distinct()
    )
    return sorted({c for c in codes if c})


def compute_total_career_experience_months(professional):
    """Based On (sheet): All job and project dates — same overlap-merge
    method as Calendar Experience, applied person-wide. Per the explicit
    spec given, this is computed purely from ProjectRecord across every
    scope (no scope filter), using the same start-to-end span as Calendar
    Experience. NOTE: EmploymentRecord dates are NOT folded in here even
    though the sheet's own wording says 'job and project dates' — the
    explicit spec only described project-record logic for this field; say
    the word if EmploymentRecord should be unioned in too."""
    records = ProjectRecord.objects.filter(
        professional=professional,
        verification_status__in=FIXED_FIELD_STATUSES,
    ).order_by("start_date")
    return _span_in_months((r.start_date, r.end_date) for r in records)


def build_headline(professional):
    """Based On: Verified level, industry, scope. Fixed template fill —
    per the sheet this is 'drafted automatically... editable', not a
    tenant-tunable rule. Level and scope come off the professional's
    highest-ranked ProfessionalScope (same 'best_scope' pick
    build_render_tokens uses); industry from primary_industry. Note this
    drops primary_role from the template — the sheet's Based On column
    for this field lists only level/industry/scope, not role."""
    best_scope = (
        ProfessionalScope.objects.filter(professional=professional)
        .select_related("current_qualion_level", "scope")
        .order_by("-current_qualion_level__sort_order")
        .first()
    )
    level_label = (
        best_scope.current_qualion_level.label
        if best_scope and best_scope.current_qualion_level
        else None
    )
    scope_label = best_scope.scope.scope_name if best_scope else None
    industry_label = professional.primary_industry.label if professional.primary_industry_id else None
    parts = [level_label, industry_label, scope_label]
    return " — ".join(p for p in parts if p)


def build_responsibility_bullets(project):
    """Based On: Structured activity fields on each project. Composes
    responsibilities text from role_title, each linked ProjectScope's
    scope/authority_action/activity_summary and standards_applied —
    drafted from structured data instead of free text, per the sheet.

    CAUTION: experience.ProjectRecord.responsibilities is otherwise a
    candidate-entered free-text field (min 100 chars, required at
    submission) — this only ever fills it when it is currently blank.
    An existing candidate-written value is never overwritten here."""
    parts = []
    if project.role_title_id:
        parts.append(f"Worked as {project.role_title.label} on {project.project_name}.")
    else:
        parts.append(f"Contributed to {project.project_name}.")
    scope_bits = []
    for ps in project.project_scopes.select_related("scope", "authority_action").all():
        bit = ps.scope.scope_name
        if ps.authority_action:
            bit += f" ({ps.authority_action.label})"
        if ps.activity_summary:
            bit += f": {ps.activity_summary}"
        scope_bits.append(bit)
    if scope_bits:
        parts.append("Scope of work: " + "; ".join(scope_bits) + ".")
    if project.standards_applied:
        parts.append("Standards applied: " + ", ".join(str(s) for s in project.standards_applied) + ".")
    return " ".join(parts)


def build_summary(professional):
    """Based On: The person's full structured profile. Fixed template fill
    from key strengths, primary role, best-scope level/experience and the
    top verified achievements — not a tenant-tunable rule. Product/copy
    wording is intentionally simple here; refine the sentence templates as
    needed without touching the calculation engine's plumbing."""
    tokens = build_render_tokens(professional)
    sentences = []
    if tokens.get("key_strengths"):
        sentences.append(tokens["key_strengths"].strip().rstrip("."))
    role = tokens.get("primary_role.label")
    level = tokens.get("current_qualion_level.label")
    months = tokens.get("calendar_experience_months")
    if role or level:
        bit = f"{role or 'Professional'}"
        if level:
            bit += f" at {level} level"
        if months:
            bit += f" with {months} months' verified experience"
        sentences.append(bit)
    achievements = list(
        ProjectRecord.objects.filter(
            professional=professional, verification_status__in=FIXED_FIELD_STATUSES
        )
        .exclude(achievements="")
        .order_by("-verified_field_days")
        .values_list("achievements", flat=True)[:3]
    )
    sentences.extend(a.strip().rstrip(".") for a in achievements if a)
    return ". ".join(s for s in sentences if s) + ("." if sentences else "")


def compute_credential_status(credential, today=None):
    """Based On: Certification expiry date vs. current date. Pure function —
    only ever auto-transitions among ACTIVE/EXPIRING_SOON/EXPIRED. Never
    touches SUSPENDED/REVOKED/PENDING_VERIFICATION/DRAFT/ARCHIVED: per the
    sheet, 'an expired credential should not simply be overridden to
    Active — corrected evidence must be supplied' via the human
    override/evidence path instead. Returns None when nothing should
    change."""
    AUTO_STATES = {"ACTIVE", "EXPIRING_SOON", "EXPIRED"}
    if credential.status not in AUTO_STATES or not credential.expiry_date:
        return None
    today = today or timezone.now().date()
    if credential.expiry_date < today:
        new_status = "EXPIRED"
    elif credential.expiry_date <= today + timedelta(days=30):
        new_status = "EXPIRING_SOON"
    else:
        new_status = "ACTIVE"
    return new_status if new_status != credential.status else None


# ---------------------------------------------------------------------
# ReferenceValue rank helpers
# ---------------------------------------------------------------------

def _rank_of_code(option_set_code, code):
    rv = ReferenceValue.objects.filter(option_set__option_type=option_set_code, code=code).first()
    if not rv:
        raise CalculationError(f"No ReferenceValue with option_set={option_set_code}, code={code}")
    return rv.sort_order


def _rank_of_instance(instance):
    return instance.sort_order if instance else None


# ---------------------------------------------------------------------
# Rule set lookup + evaluation
# ---------------------------------------------------------------------

def get_published_rule_set(tenant, calculation_field_code, scope=None):
    qs = CalculationRuleSet.objects.filter(
        tenant=tenant,
        calculation_field_code=calculation_field_code,
        status="PUBLISHED",
    )
    if scope is not None:
        rule_set = qs.filter(scope=scope).order_by("-version").first()
        if rule_set:
            return rule_set
    return qs.filter(scope__isnull=True).order_by("-version").first()


def _eval_condition(key_expr, expected, context):
    if key_expr in ("has_credential", "template_tokens", "source_table", "aggregation", "filter"):
        return None  # handled elsewhere / informational, not a boolean test
    key, _, op = key_expr.rpartition("__")
    if not key:
        key, op = key_expr, "eq"
    actual = context.get(key)
    if actual is None:
        return False
    if key in OPTION_SET_FOR_KEY and isinstance(expected, str):
        expected = _rank_of_code(OPTION_SET_FOR_KEY[key], expected)
    ops = {
        "gte": lambda a, e: a >= e,
        "lte": lambda a, e: a <= e,
        "gt": lambda a, e: a > e,
        "lt": lambda a, e: a < e,
        "eq": lambda a, e: a == e,
        "in": lambda a, e: a in e,
    }
    return ops.get(op, ops["eq"])(actual, expected)


def evaluate_conditions(conditions, context, match_type="ALL_CONDITIONS"):
    if not conditions:
        return True
    results = []
    for key_expr, expected in conditions.items():
        if key_expr == "has_credential":
            results.append(bool(context.get("has_active_certification")))
            continue
        outcome = _eval_condition(key_expr, expected, context)
        if outcome is not None:
            results.append(outcome)
    if not results:
        return True
    return all(results) if match_type == "ALL_CONDITIONS" else any(results)


def evaluate_rule_set(rule_set, context):
    """Returns (rule, concluded_value) for the first matching rule, or
    (None, None) if nothing matches."""
    for rule in rule_set.rules.filter(is_active=True).order_by("sequence"):
        if evaluate_conditions(rule.conditions, context, rule.match_type):
            return rule, rule.concluded_value
    return None, None


def render_template(template, tokens):
    try:
        return template.format(**tokens)
    except KeyError as exc:
        raise CalculationError(f"Template references unknown token: {exc}")


# ---------------------------------------------------------------------
# Context builders
# ---------------------------------------------------------------------

def _get_or_create_prof_scope(professional, scope, tenant):
    """Get-or-create the ProfessionalScope row for professional+scope.
    current_qualion_level/current_authority_status/scope are all nullable
    on the model now, so new rows are created without inventing a default
    level or authority — nothing here needs to guess at catalog seed data
    anymore. Fields that actually depend on a qualion level being present
    (currently just Headline) are skipped via CalculationSkipped instead,
    see _has_any_qualion_level below."""
    prof_scope, _ = ProfessionalScope.objects.get_or_create(
        professional=professional,
        scope=scope,
        defaults={"tenant": tenant},
    )
    return prof_scope


class CalculationSkipped(Exception):
    """Raised by a fixed-field handler to say "nothing to compute yet,
    this isn't an error" — e.g. no qualion level (current or previous)
    recorded anywhere for this professional. _run_one_fixed_field turns
    this into status=SKIPPED, distinct from status=ERROR."""


def _has_any_qualion_level(professional):
    """True if this professional has a qualion level recorded anywhere:
    either "current" (ProfessionalScope.current_qualion_level, any scope)
    or "previous" (a CompetencyAssessment — previous_level, recommended_level
    or approved_level — for any of their scopes). Used to gate fields whose
    Based On column explicitly lists level as an input (currently just
    Headline) so they're skipped rather than computed with a missing level
    silently dropped from the output."""
    if ProfessionalScope.objects.filter(
        professional=professional, current_qualion_level__isnull=False
    ).exists():
        return True
    return CompetencyAssessment.objects.filter(
        professional_scope__professional=professional
    ).filter(
        models.Q(previous_level__isnull=False)
        | models.Q(recommended_level__isnull=False)
        | models.Q(approved_level__isnull=False)
    ).exists()


def build_scope_context(professional, scope, tenant):
    prof_scope = _get_or_create_prof_scope(professional, scope, tenant)
    has_active_cert = CredentialRecord.objects.filter(
        professional=professional,
        record_type="CERTIFICATION",
        status="ACTIVE",
        related_scope=scope,
    ).exists()
    context = {
        "calendar_experience_months": compute_calendar_experience_months(professional, scope),
        "verified_field_days": float(compute_verified_field_days(professional, scope)),
        "current_authority_status": _rank_of_instance(prof_scope.current_authority_status),
        "complexity_rating": _rank_of_instance(prof_scope.complexity_rating),
        "has_active_certification": has_active_cert,
    }
    return prof_scope, context


def build_classification_context(professional):
    best_scope = (
        ProfessionalScope.objects.filter(professional=professional)
        .select_related("current_qualion_level", "current_authority_status")
        .order_by("-current_qualion_level__sort_order")
        .first()
    )
    latest_assessment = (
        CompetencyAssessment.objects.filter(
            professional_scope__professional=professional, decision="APPROVED"
        )
        .order_by("-approved_at")
        .first()
    )
    return {
        "current_qualion_level": _rank_of_instance(best_scope.current_qualion_level) if best_scope else None,
        "current_authority_status": _rank_of_instance(best_scope.current_authority_status) if best_scope else None,
        "ethics_independence_score": float(latest_assessment.ethics_independence_score) if latest_assessment else None,
    }


def build_render_tokens(professional):
    best_scope = (
        ProfessionalScope.objects.filter(professional=professional)
        .select_related("current_qualion_level")
        .order_by("-current_qualion_level__sort_order")
        .first()
    )
    return {
        "primary_role.label": professional.primary_role.label if professional.primary_role_id else "",
        "current_qualion_level.label": best_scope.current_qualion_level.label if best_scope else "",
        "primary_industry.label": professional.primary_industry.label if professional.primary_industry_id else "",
        "key_strengths": professional.key_strengths or "",
        "calendar_experience_months": str(
            compute_calendar_experience_months(professional, professional.primary_scope)
            if professional.primary_scope_id
            else ""
        ),
    }


# ---------------------------------------------------------------------
# Field handlers: (professional, scope, tenant) -> dict describing what to write
# ---------------------------------------------------------------------

def _resolve_value_for_field(target_model, field_name, raw_value):
    """Turns a JSON concluded_value into the actual value to setattr."""
    field = target_model._meta.get_field(field_name)
    if isinstance(raw_value, dict) and "value" in raw_value and not field.is_relation:
        raw_value = raw_value["value"]
    elif isinstance(raw_value, dict) and len(raw_value) == 1 and not field.is_relation:
        raw_value = next(iter(raw_value.values()))

    if field.is_relation:
        code = raw_value.get("code") if isinstance(raw_value, dict) else raw_value
        related_model = field.related_model
        try:
            return related_model.objects.get(code=code)
        except related_model.DoesNotExist:
            raise CalculationError(f"No {related_model.__name__} found with code={code!r}")
    if isinstance(field, models.BooleanField):
        return bool(raw_value)
    return raw_value


def handle_calendar_experience(professional, scope, tenant):
    prof_scope, context = build_scope_context(professional, scope, tenant)
    value = context["calendar_experience_months"]
    return {
        "target_instance": prof_scope,
        "field_name": "calendar_experience_months",
        "resolved_value": value,
        "new_value_raw": value,
        "ruleset_version": "",
        "rule_label": "system aggregation (union of verified project dates)",
    }


def handle_verified_field_days(professional, scope, tenant):
    prof_scope, context = build_scope_context(professional, scope, tenant)
    value = Decimal(str(context["verified_field_days"]))
    return {
        "target_instance": prof_scope,
        "field_name": "verified_field_days",
        "resolved_value": value,
        "new_value_raw": float(value),
        "ruleset_version": "",
        "rule_label": "system aggregation (sum of approved exposure days)",
    }


def _handle_rule_based_scope_field(professional, scope, tenant, calculation_field_code, field_name):
    prof_scope, context = build_scope_context(professional, scope, tenant)
    rule_set = get_published_rule_set(tenant, calculation_field_code, scope)
    if not rule_set:
        raise CalculationError(
            f"No PUBLISHED CalculationRuleSet for tenant={tenant}, "
            f"calculation_field_code={calculation_field_code}, scope={scope}."
        )
    rule, concluded_value = evaluate_rule_set(rule_set, context)
    if concluded_value is None:
        raise CalculationError("No rule matched the professional's current parameters.")
    resolved = _resolve_value_for_field(ProfessionalScope, field_name, concluded_value)
    return {
        "target_instance": prof_scope,
        "field_name": field_name,
        "resolved_value": resolved,
        "new_value_raw": concluded_value,
        "ruleset_version": rule_set.version,
        "rule_label": rule.label,
    }


def handle_qualion_level(professional, scope, tenant):
    return _handle_rule_based_scope_field(
        professional, scope, tenant, CalculatedFieldCode.QUALION_LEVEL, "current_qualion_level"
    )


def handle_deployability(professional, scope, tenant):
    return _handle_rule_based_scope_field(
        professional, scope, tenant, CalculatedFieldCode.DEPLOYABILITY_FLAG, "is_deployable"
    )


def _handle_rule_based_profile_field(professional, calculation_field_code, field_name, context, tokens=None):
    tenant = professional.tenant
    rule_set = get_published_rule_set(tenant, calculation_field_code, scope=None)
    if not rule_set:
        raise CalculationError(
            f"No PUBLISHED tenant-wide CalculationRuleSet for calculation_field_code={calculation_field_code}."
        )
    rule, concluded_value = evaluate_rule_set(rule_set, context)
    if concluded_value is None:
        raise CalculationError("No rule matched the professional's current parameters.")

    if "template" in concluded_value:
        rendered = render_template(concluded_value["template"], tokens or {})
        resolved = rendered
        new_value_raw = rendered
    else:
        resolved = _resolve_value_for_field(ProfessionalProfile, field_name, concluded_value)
        new_value_raw = concluded_value

    return {
        "target_instance": professional,
        "field_name": field_name,
        "resolved_value": resolved,
        "new_value_raw": new_value_raw,
        "ruleset_version": rule_set.version,
        "rule_label": rule.label,
    }


def handle_headline(professional, scope, tenant):
    if not _has_any_qualion_level(professional):
        raise CalculationSkipped(
            "No qualion level recorded yet (current ProfessionalScope."
            "current_qualion_level, or a previous_level/recommended_level/"
            "approved_level on any CompetencyAssessment) — Headline's Based "
            "On column requires level, so it's skipped rather than computed "
            "with that part silently missing."
        )
    value = build_headline(professional)
    return {
        "target_instance": professional,
        "field_name": "headline",
        "resolved_value": value,
        "new_value_raw": value,
        "ruleset_version": "",
        "rule_label": "system template (level — industry — scope)",
    }


def handle_summary(professional, scope, tenant):
    value = build_summary(professional)
    # summary_source rides along on the same instance/save() as "summary" —
    # apply_calculated_value's target_instance.save() persists the whole
    # row, not just field_name, so setting it here is enough (item 6.1).
    professional.summary_source = ProfessionalProfile.SummarySource.SYSTEM_GENERATED
    return {
        "target_instance": professional,
        "field_name": "summary",
        "resolved_value": value,
        "new_value_raw": value,
        "ruleset_version": "",
        "rule_label": "system template (strengths + role/level + top achievements); summary_source -> SYSTEM_GENERATED",
    }


def handle_verified_project_count(professional, scope, tenant):
    prof_scope = _get_or_create_prof_scope(professional, scope, tenant)
    value = compute_verified_project_count(professional, scope)
    return {
        "target_instance": prof_scope,
        "field_name": "verified_project_count",
        "resolved_value": value,
        "new_value_raw": value,
        "ruleset_version": "",
        "rule_label": "system aggregation (count of distinct verified projects)",
    }


def handle_highest_authority_reached(professional, scope, tenant):
    prof_scope = _get_or_create_prof_scope(professional, scope, tenant)
    resolved = compute_highest_authority_reached(professional, scope)
    if resolved is None:
        raise CalculationError(
            "No ProjectScope with an authority_action found for this "
            "professional+scope yet (checked FIXED_FIELD_STATUSES)."
        )
    return {
        "target_instance": prof_scope,
        "field_name": "highest_authority_reached",
        "resolved_value": resolved,
        "new_value_raw": {"code": resolved.code},
        "ruleset_version": "",
        "rule_label": "system aggregation (max-rank ProjectScope.authority_action ever recorded)",
    }


def handle_industries_served(professional, scope, tenant):
    codes = compute_industries_served(professional)
    return {
        "target_instance": professional,
        "field_name": "industries_served",
        "resolved_value": codes,
        "new_value_raw": codes,
        "ruleset_version": "",
        "rule_label": "system aggregation (distinct industries behind verified scopes)",
    }


def handle_total_career_experience(professional, scope, tenant):
    value = compute_total_career_experience_months(professional)
    return {
        "target_instance": professional,
        "field_name": "total_career_experience_months",
        "resolved_value": value,
        "new_value_raw": value,
        "ruleset_version": "",
        "rule_label": "system aggregation (union of verified employment dates, person-wide)",
    }


def handle_primary_role(professional, scope, tenant):
    primary_role_id, _ = compute_primary_and_additional_roles(professional)
    if primary_role_id is None:
        raise CalculationError("No verified project records with a role_title to derive a primary role from.")
    resolved = ReferenceValue.objects.get(pk=primary_role_id)
    return {
        "target_instance": professional,
        "field_name": "primary_role",
        "resolved_value": resolved,
        "new_value_raw": {"code": resolved.code},
        "ruleset_version": "",
        "rule_label": "system aggregation (role with most verified field days)",
    }


def handle_additional_roles(professional, scope, tenant):
    _, additional_ids = compute_primary_and_additional_roles(professional)
    codes = list(ReferenceValue.objects.filter(pk__in=additional_ids).values_list("code", flat=True))
    return {
        "target_instance": professional,
        "field_name": "additional_roles",
        "resolved_value": codes,
        "new_value_raw": codes,
        "ruleset_version": "",
        "rule_label": "system aggregation (other roles above field-day floor)",
    }


def handle_classification(professional, scope, tenant):
    context = build_classification_context(professional)
    return _handle_rule_based_profile_field(
        professional,
        CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION,
        "current_classification",
        context,
    )


FIELD_HANDLERS = {
    CalculatedFieldCode.CALENDAR_EXPERIENCE: handle_calendar_experience,
    CalculatedFieldCode.VERIFIED_FIELD_DAYS: handle_verified_field_days,
    CalculatedFieldCode.VERIFIED_PROJECT_COUNT: handle_verified_project_count,
    CalculatedFieldCode.HIGHEST_AUTHORITY_REACHED: handle_highest_authority_reached,
    CalculatedFieldCode.QUALION_LEVEL: handle_qualion_level,
    CalculatedFieldCode.DEPLOYABILITY_FLAG: handle_deployability,
    CalculatedFieldCode.PROFESSIONAL_HEADLINE: handle_headline,
    CalculatedFieldCode.PROFESSIONAL_SUMMARY: handle_summary,
    CalculatedFieldCode.PRIMARY_ROLE: handle_primary_role,
    CalculatedFieldCode.ADDITIONAL_ROLES: handle_additional_roles,
    CalculatedFieldCode.INDUSTRIES_SERVED: handle_industries_served,
    CalculatedFieldCode.TOTAL_CAREER_EXPERIENCE: handle_total_career_experience,
    CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION: handle_classification,
}


# ---------------------------------------------------------------------
# Apply + log (shared by both the calculate API and the override API)
# ---------------------------------------------------------------------

def _serialize_current_value(target_instance, field_name):
    field = target_instance.__class__._meta.get_field(field_name)
    current = getattr(target_instance, field_name)
    if field.is_relation:
        return {"code": current.code} if current else None
    if isinstance(current, Decimal):
        return float(current)
    return current


def sync_user_candidate_mentor_flags(professional, classification_value):
    """Keep accounts.UserTbl.is_candidate/is_mentor in lockstep with
    ProfessionalProfile.current_classification.

    current_classification is the single field the calculation engine
    and the override API actually write to (see TARGET_FIELD_NAME). The
    boolean pair on UserTbl is a separate table/row and nothing was ever
    setting it, so it silently stayed at its default (False, False) no
    matter what the classification engine concluded.

    A professional can be both a candidate and a mentor at once
    (Classification.BOTH), so this is two independent booleans, not one
    flag flip — CANDIDATE/MENTOR/BOTH/UNCLASSIFIED all map to a distinct
    (is_candidate, is_mentor) pair.
    """
    user = professional.user
    is_candidate = classification_value in (
        ProfessionalProfile.Classification.CANDIDATE,
        ProfessionalProfile.Classification.Both,
    )
    is_mentor = classification_value in (
        ProfessionalProfile.Classification.MENTOR,
        ProfessionalProfile.Classification.Both,
    )
    if user.is_candidate != is_candidate or user.is_mentor != is_mentor:
        user.is_candidate = is_candidate
        user.is_mentor = is_mentor
        user.save(update_fields=["is_candidate", "is_mentor"])


def apply_calculated_value(
    *,
    tenant,
    professional,
    target_instance,
    field_name,
    calculation_field_code,
    resolved_value,
    new_value_raw,
    ruleset_version="",
    change_source="SYSTEM_RECALCULATION",
    override=None,
    changed_by=None,
    effective_from=None,
):
    previous_raw = _serialize_current_value(target_instance, field_name)

    setattr(target_instance, field_name, resolved_value)
    if hasattr(target_instance, "last_recalculated_at") and change_source == "SYSTEM_RECALCULATION":
        target_instance.last_recalculated_at = timezone.now()
    target_instance.save()

    # CANDIDATE_MENTOR_CLASSIFICATION only ever wrote current_classification
    # on ProfessionalProfile; it never touched accounts.UserTbl.is_candidate/
    # is_mentor, which is why those flags never moved from either the
    # system calculate API or an approved override. Sync them here so both
    # call sites (calculate + override-approve) stay covered from one place.
    if calculation_field_code == CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION:
        sync_user_candidate_mentor_flags(professional, resolved_value)

    history = CalculatedFieldValueHistory.objects.create(
        tenant=tenant,
        content_type=ContentType.objects.get_for_model(target_instance.__class__),
        object_id=target_instance.pk,
        field_name=field_name,
        calculation_field_code=calculation_field_code,
        professional=professional,
        previous_value=previous_raw,
        new_value=new_value_raw,
        change_source=change_source,
        override=override,
        changed_by=changed_by,
        effective_from=effective_from or timezone.now().date(),
        recalculation_ruleset_version=ruleset_version or "",
    )
    return previous_raw, history


# ---------------------------------------------------------------------
# calculate-fixed: one call, all 11 fixed-formula fields, no rule set
# ---------------------------------------------------------------------

def _run_one_fixed_field(professional, scope, tenant, calculation_field_code):
    """Runs a single FIXED_FIELD_CODES handler + apply_calculated_value,
    normalising success/failure into one result dict instead of raising —
    so one field failing (e.g. no verified data yet) doesn't abort the rest
    of the batch."""
    try:
        result = FIELD_HANDLERS[calculation_field_code](professional, scope, tenant)
        previous_raw, history = apply_calculated_value(
            tenant=tenant,
            professional=professional,
            target_instance=result["target_instance"],
            field_name=result["field_name"],
            calculation_field_code=calculation_field_code,
            resolved_value=result["resolved_value"],
            new_value_raw=result["new_value_raw"],
            ruleset_version=result["ruleset_version"],
            change_source="SYSTEM_RECALCULATION",
        )
        return {
            "calculation_field_code": calculation_field_code,
            "status": "SAVED",
            "scope": scope.pk if scope else None,
            "field_name": result["field_name"],
            "previous_value": previous_raw,
            "new_value": result["new_value_raw"],
            "rule_applied": result["rule_label"],
            "history_id": history.pk,
        }
    except CalculationSkipped as exc:
        return {
            "calculation_field_code": calculation_field_code,
            "status": "SKIPPED",
            "scope": scope.pk if scope else None,
            "message": str(exc),
        }
    except CalculationError as exc:
        return {
            "calculation_field_code": calculation_field_code,
            "status": "ERROR",
            "scope": scope.pk if scope else None,
            "message": str(exc),
        }


def calculate_fixed_fields_for_professional(professional, scopes=None):
    """Recalculates all 12 fixed-formula fields for one professional in a
    single pass:
      - Scope-level fields (Calendar Experience, Verified Field Days,
        Verified Project Count, Highest Authority Reached) run once per
        scope. Defaults to every distinct ScopeCatalog behind this
        professional's ProjectScope rows (i.e. discovered from their
        project experience, not from pre-existing ProfessionalScope
        rows) — a ProfessionalScope row is created for each one that
        doesn't already exist. Pass explicit ScopeCatalog instances to
        override that discovery.
      - Profile-level fields (Headline, Summary, Primary Role, Additional
        Roles, Industries Served, Total Career Experience) run once.
      - Credential Status runs once per ACTIVE/EXPIRING_SOON/EXPIRED
        CredentialRecord with an expiry_date, each logged against that
        credential row.
      - Project Responsibility Bullets runs once per ProjectRecord whose
        responsibilities field is currently blank (never overwrites an
        existing candidate-written value), each logged against that
        project row.

    Returns a dict: {"scopes": [...], "profile": [...],
    "credentials": [...], "responsibilities": [...]}, each entry shaped
    like one field's result.
    """
    tenant = professional.tenant
    if scopes is None:
        scope_ids = (
            ProjectScope.objects.filter(project__professional=professional)
            .values_list("scope_id", flat=True)
            .distinct()
        )
        scopes = list(ScopeCatalog.objects.filter(pk__in=scope_ids))

    scope_results = []
    for scope in scopes:
        for code in (
            CalculatedFieldCode.CALENDAR_EXPERIENCE,
            CalculatedFieldCode.VERIFIED_FIELD_DAYS,
            CalculatedFieldCode.VERIFIED_PROJECT_COUNT,
            CalculatedFieldCode.HIGHEST_AUTHORITY_REACHED,
        ):
            scope_results.append(_run_one_fixed_field(professional, scope, tenant, code))

    profile_results = [
        _run_one_fixed_field(professional, None, tenant, code)
        for code in (
            CalculatedFieldCode.PROFESSIONAL_HEADLINE,
            CalculatedFieldCode.PROFESSIONAL_SUMMARY,
            CalculatedFieldCode.PRIMARY_ROLE,
            CalculatedFieldCode.ADDITIONAL_ROLES,
            CalculatedFieldCode.INDUSTRIES_SERVED,
            CalculatedFieldCode.TOTAL_CAREER_EXPERIENCE,
        )
    ]

    credential_results = []
    for credential in CredentialRecord.objects.filter(
        professional=professional,
        status__in=["ACTIVE", "EXPIRING_SOON", "EXPIRED"],
        expiry_date__isnull=False,
    ):
        new_status = compute_credential_status(credential)
        if new_status is None:
            continue
        previous_raw, history = apply_calculated_value(
            tenant=tenant,
            professional=professional,
            target_instance=credential,
            field_name="status",
            calculation_field_code=CalculatedFieldCode.CREDENTIAL_STATUS,
            resolved_value=new_status,
            new_value_raw=new_status,
            ruleset_version="",
            change_source="SYSTEM_RECALCULATION",
        )
        credential_results.append(
            {
                "calculation_field_code": CalculatedFieldCode.CREDENTIAL_STATUS,
                "status": "SAVED",
                "credential_id": credential.pk,
                "field_name": "status",
                "previous_value": previous_raw,
                "new_value": new_status,
                "rule_applied": "system aggregation (expiry date vs. today)",
                "history_id": history.pk,
            }
        )

    responsibility_results = []
    for project in ProjectRecord.objects.filter(professional=professional, responsibilities=""):
        text = build_responsibility_bullets(project)
        if len(text) < 100:
            responsibility_results.append(
                {
                    "calculation_field_code": CalculatedFieldCode.PROJECT_RESPONSIBILITY_BULLETS,
                    "status": "ERROR",
                    "project_id": project.pk,
                    "message": "Not enough structured data (role_title/project_scopes/"
                    "standards_applied) to draft the required 100+ characters; "
                    "needs candidate input instead.",
                }
            )
            continue
        previous_raw, history = apply_calculated_value(
            tenant=tenant,
            professional=professional,
            target_instance=project,
            field_name="responsibilities",
            calculation_field_code=CalculatedFieldCode.PROJECT_RESPONSIBILITY_BULLETS,
            resolved_value=text,
            new_value_raw=text,
            ruleset_version="",
            change_source="SYSTEM_RECALCULATION",
        )
        responsibility_results.append(
            {
                "calculation_field_code": CalculatedFieldCode.PROJECT_RESPONSIBILITY_BULLETS,
                "status": "SAVED",
                "project_id": project.pk,
                "field_name": "responsibilities",
                "previous_value": previous_raw,
                "new_value": text,
                "rule_applied": "system template (role + scope/authority + standards_applied); "
                "only fills a currently-blank responsibilities field",
                "history_id": history.pk,
            }
        )

    return {
        "scopes": scope_results,
        "profile": profile_results,
        "credentials": credential_results,
        "responsibilities": responsibility_results,
    }