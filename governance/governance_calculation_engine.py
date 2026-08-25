"""governance/services/calculation_engine.py

The engine behind the two new endpoints:
  1. POST /api/governance/calculated-fields/calculate/  -> system decides
     a value from real data + admin rules, writes it to the main/related
     table, logs CalculatedFieldValueHistory (SYSTEM_RECALCULATION).
  2. POST /api/governance/calculated-fields/override/    -> admin/reviewer
     override, writes CalculatedFieldOverride, and if decision=APPROVED
     in the same call, also writes the field + logs history
     (OVERRIDE_APPROVED).

Scope: only the 9 of 15 calculation_field_code values that already have a
real destination field are wired up here (see FIELD_HANDLERS below).
VERIFIED_PROJECT_COUNT, HIGHEST_AUTHORITY_REACHED, INDUSTRIES_SERVED,
TOTAL_CAREER_EXPERIENCE, CREDENTIAL_STATUS (as an enum) and the enum
version of DEPLOYABILITY_FLAG are NOT wired up because the model fields
they'd write to don't exist yet (flagged previously). Calling the API for
those raises CalculationError with a clear message instead of failing
silently or guessing a field name.
"""

from datetime import date
from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from catalog.models import ReferenceValue
from competency.models import ProfessionalScope
from competency.models import CompetencyAssessment
from experience.models import ExposureLog, ProjectRecord
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
    CalculatedFieldCode.QUALION_LEVEL,
    CalculatedFieldCode.DEPLOYABILITY_FLAG,
}
PROFILE_FIELDS = {
    CalculatedFieldCode.PROFESSIONAL_HEADLINE,
    CalculatedFieldCode.PROFESSIONAL_SUMMARY,
    CalculatedFieldCode.PRIMARY_ROLE,
    CalculatedFieldCode.ADDITIONAL_ROLES,
    CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION,
}
SUPPORTED_FIELDS = SCOPED_FIELDS | PROFILE_FIELDS

TARGET_FIELD_NAME = {
    CalculatedFieldCode.CALENDAR_EXPERIENCE: "calendar_experience_months",
    CalculatedFieldCode.VERIFIED_FIELD_DAYS: "verified_field_days",
    CalculatedFieldCode.QUALION_LEVEL: "current_qualion_level",
    CalculatedFieldCode.DEPLOYABILITY_FLAG: "is_deployable",
    CalculatedFieldCode.PROFESSIONAL_HEADLINE: "headline",
    CalculatedFieldCode.PROFESSIONAL_SUMMARY: "summary",
    CalculatedFieldCode.PRIMARY_ROLE: "primary_role",
    CalculatedFieldCode.ADDITIONAL_ROLES: "additional_roles",
    CalculatedFieldCode.CANDIDATE_MENTOR_CLASSIFICATION: "current_classification",
}

# Which ReferenceValue.option_set a given context key/target field ranks against
OPTION_SET_FOR_KEY = {
    "current_authority_status": "AUTHORITY_STATUS",
    "complexity_rating": "COMPLEXITY",
    "current_qualion_level": "QUALION_LEVEL",
}

VERIFIED_STATES = ["VERIFIED", "VALIDATED"]


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


def compute_calendar_experience_months(professional, scope):
    today = timezone.now().date()
    projects = (
        ProjectRecord.objects.filter(
            professional=professional,
            project_scopes__scope=scope,
            project_scopes__verification_status__in=VERIFIED_STATES,
            verification_status__in=VERIFIED_STATES,
        )
        .distinct()
    )
    intervals = [
        (p.start_date, today if p.is_current else (p.end_date or today))
        for p in projects
    ]
    return _merge_date_ranges_to_months(intervals)


def compute_verified_field_days(professional, scope):
    total = ExposureLog.objects.filter(
        professional=professional,
        project_scope__scope=scope,
        status="APPROVED",
    ).aggregate(total=Sum("day_fraction"))["total"]
    return total or Decimal("0.00")


def compute_primary_and_additional_roles(professional, min_additional_field_days=20):
    rows = (
        ProjectRecord.objects.filter(
            professional=professional,
            verification_status__in=VERIFIED_STATES,
            role_title__isnull=False,
        )
        .values("role_title")
        .annotate(total_days=Sum("verified_field_days"))
        .order_by("-total_days")
    )
    rows = list(rows)
    if not rows:
        return None, []
    primary_role_id = rows[0]["role_title"]
    additional_role_ids = [
        r["role_title"] for r in rows[1:] if (r["total_days"] or 0) >= min_additional_field_days
    ]
    return primary_role_id, additional_role_ids


# ---------------------------------------------------------------------
# ReferenceValue rank helpers
# ---------------------------------------------------------------------

def _rank_of_code(option_set_code, code):
    rv = ReferenceValue.objects.filter(option_set__code=option_set_code, code=code).first()
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

def build_scope_context(professional, scope, tenant):
    prof_scope, _ = ProfessionalScope.objects.get_or_create(
        professional=professional,
        scope=scope,
        defaults={
            "tenant": tenant,
            "current_qualion_level": ReferenceValue.objects.filter(
                option_set__code="QUALION_LEVEL", code="L0"
            ).first(),
            "current_authority_status": ReferenceValue.objects.filter(
                option_set__code="AUTHORITY_STATUS", code="OBSERVER"
            ).first(),
        },
    )
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
    tokens = build_render_tokens(professional)
    context = {"min_completeness_percent": 100}  # headline rule conditions are template-only in practice
    return _handle_rule_based_profile_field(
        professional, CalculatedFieldCode.PROFESSIONAL_HEADLINE, "headline", context, tokens
    )


def handle_summary(professional, scope, tenant):
    tokens = build_render_tokens(professional)
    context = {"min_completeness_percent": 100}
    return _handle_rule_based_profile_field(
        professional, CalculatedFieldCode.PROFESSIONAL_SUMMARY, "summary", context, tokens
    )


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
    CalculatedFieldCode.QUALION_LEVEL: handle_qualion_level,
    CalculatedFieldCode.DEPLOYABILITY_FLAG: handle_deployability,
    CalculatedFieldCode.PROFESSIONAL_HEADLINE: handle_headline,
    CalculatedFieldCode.PROFESSIONAL_SUMMARY: handle_summary,
    CalculatedFieldCode.PRIMARY_ROLE: handle_primary_role,
    CalculatedFieldCode.ADDITIONAL_ROLES: handle_additional_roles,
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
