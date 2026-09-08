from datetime import date
from decimal import Decimal

from django.db.models import Q

from professionals.models import ProfessionalProfile
from professionals.models import CredentialRecord

from experience.models import (
    EmploymentRecord,
    ProjectRecord,
    ProjectScope,
    ScopeResponse,
    ExposureLog,
)

from accounts.models import ConsentRecord

from resumes.models import ResumeTemplate


class ResumeBuilderService:
    """
    Dynamic Resume Builder Service.

    Uses ProfessionalProfile.id as the primary key.

    This service only builds resume data.
    It does NOT create ResumeGeneration records.
    """

    def __init__(
        self,
        professional,
        request=None,
        client_organization_id=None,
        template_id=None,
        scope_ids=None,
    ):

        self.professional = professional
        self.request = request

        self.client_organization_id = (
            client_organization_id
        )

        self.template_id = template_id

        self.scope_ids = scope_ids or []

        self.template = None

        if self.template_id:
            self.template = self._get_template()

    # =========================================================
    # MAIN BUILD
    # =========================================================

    def build(self):

        return {
            "professional_profile_id": (
                self.professional.id
            ),

            "template": self._template_data(),

            "header": self._header(),

            "personal_details": (
                self._personal_details()
            ),

            "profile": self._profile(),

            "education": self._education(),

            "certifications": (
                self._certifications()
            ),

            "training": self._training(),

            "employment": self._employment(),

            "projects": self._projects(),

            "scope_expertise": (
                self._scope_expertise()
            ),

            "skills": self._skills(),

            "languages": self._languages(),

            "references": self._references(),

            "client_approvals": (
                self._client_approvals()
            ),

            "declaration": self._declaration(),

            "meta": {
                "builder_version": "1.0",
                "template_applied": (
                    self.template is not None
                ),
            },
        }

    # =========================================================
    # TEMPLATE
    # =========================================================

    def _get_template(self):

        queryset = ResumeTemplate.objects.filter(
            is_active=True
        )

        if self.client_organization_id:

            queryset = queryset.filter(
                client_organization_id=(
                    self.client_organization_id
                )
            )

        return queryset.filter(
            pk=self.template_id
        ).first()

    # =========================================================

    def _template_data(self):

        if not self.template:
            return None

        return {
            "id": self.template.id,

            "template_code": (
                self.template.template_code
            ),

            "template_name": (
                self.template.template_name
            ),

            "version": self.template.version,

            "output_type": (
                self.template.output_type
            ),
        }

    # =========================================================
    # TEMPLATE TOKEN CHECK
    # =========================================================

    def _template_requests(self, token):

        if not self.template:
            return False

        mapping_schema = (
            self.template.mapping_schema
            or {}
        )

        return self._contains_token(
            mapping_schema,
            token
        )

    # =========================================================

    def _contains_token(
        self,
        value,
        token,
    ):

        if isinstance(value, str):

            return (
                value == token
                or token in value
            )

        if isinstance(value, list):

            return any(
                self._contains_token(
                    item,
                    token
                )
                for item in value
            )

        if isinstance(value, dict):

            return any(
                self._contains_token(
                    item,
                    token
                )
                for item in value.values()
            )

        return False

    # =========================================================
    # CONSENT
    # =========================================================

    def _has_consent(
        self,
        consent_type,
    ):

        consent = (
            ConsentRecord.objects
            .filter(
                professional=self.professional,
                consent_type=consent_type,
            )
            .order_by("-created_at")
            .first()
        )

        if not consent:
            return False

        if not consent.is_granted:
            return False

        if consent.withdrawn_at:
            return False

        return True

    # =========================================================
    # HEADER
    # =========================================================

    def _candidate_name(self):

        if self.professional.display_name:
            return (
                self.professional.display_name
                .strip()
            )

        if self.professional.preferred_name:
            return (
                self.professional.preferred_name
                .strip()
            )

        if self.professional.legal_full_name:
            return (
                self.professional.legal_full_name
                .strip()
            )

        first = (
            self.professional.first_name
            or ""
        ).strip()

        middle = (
            self.professional.middle_name
            or ""
        ).strip()

        last = (
            self.professional.last_name
            or ""
        ).strip()

        name_order = (
            self.professional.name_display_order
            or ""
        ).upper()

        if name_order in [
            "FAMILY_GIVEN",
            "LAST_FIRST",
            "SURNAME_GIVEN",
        ]:

            parts = [
                last,
                first,
                middle,
            ]

        else:

            parts = [
                first,
                middle,
                last,
            ]

        return " ".join(
            part
            for part in parts
            if part
        ).strip()

    # =========================================================

    def _header(self):

        data = {
            "candidate_name": (
                self._candidate_name()
            ),

            "professional_title": (
                self.professional.headline
                or ""
            ),
        }

        # -----------------------------------------------------
        # PHOTO
        # -----------------------------------------------------

        photo_requested = (
            self._template_requests(
                "{{person.photo_file_id}}"
            )
        )

        photo_consent = self._has_consent(
            ConsentRecord.ConsentType.CLIENT_RESUME_SHARING
        )

        if (
            photo_requested
            and photo_consent
            and self.professional.profile_photo_evidence
        ):

            data["photo_file_id"] = (
                self.professional
                .profile_photo_evidence_id
            )

        return data

    # =========================================================
    # PERSONAL DETAILS
    # =========================================================

    def _personal_details(self):

        data = {}

        sharing_consent = self._has_consent(
            ConsentRecord.ConsentType.CLIENT_RESUME_SHARING
        )

        # -----------------------------------------------------
        # NATIONALITY
        # -----------------------------------------------------

        if self._template_requests(
            "{{person.nationalities}}"
        ):

            if self.professional.nationalities:

                data["nationalities"] = (
                    self.professional.nationalities
                )

        # -----------------------------------------------------
        # LOCATION
        # -----------------------------------------------------

        if (
            self._template_requests(
                "{{person.location.city}}"
            )
            or
            self._template_requests(
                "{{person.location.country}}"
            )
        ):

            location = {}

            if self.professional.city:
                location["city"] = (
                    self.professional.city
                )

            if (
                self.professional
                .country_of_residence
            ):

                location["country"] = (
                    self.professional
                    .country_of_residence
                )

            if location:
                data["location"] = location

        # -----------------------------------------------------
        # PHONE
        # -----------------------------------------------------

        if (
            sharing_consent
            and self.professional.primary_phone
            and self._template_requests(
                "{{person.contacts.phone}}"
            )
        ):

            data["phone"] = (
                self.professional.primary_phone
            )

        # -----------------------------------------------------
        # EMAIL
        # -----------------------------------------------------

        if (
            sharing_consent
            and self.professional.personal_email
            and self._template_requests(
                "{{person.contacts.email}}"
            )
        ):

            data["email"] = (
                self.professional.personal_email
                .lower()
            )

        return data

    # =========================================================
    # PROFILE
    # =========================================================

    def _profile(self):

        total_months = (
            self.professional
            .total_career_experience_months
            or 0
        )

        return {

            "summary": (
                self.professional.summary
                or ""
            ),

            "total_calendar_experience": {

                "months": total_months,

                "years": (
                    total_months // 12
                ),

                "remaining_months": (
                    total_months % 12
                ),

                "display": (
                    self._format_experience(
                        total_months
                    )
                ),
            },

            "key_strengths": (
                self.professional.key_strengths
                or []
            ),

            "primary_role": (
                self._reference_value(
                    self.professional.primary_role
                )
            ),

            "additional_roles": (
                self.professional.additional_roles
                or []
            ),

            "relevant_scope_experience": (
                self._scope_experience()
            ),
        }

    # =========================================================
    # EXPERIENCE FORMAT
    # =========================================================

    def _format_experience(
        self,
        months,
    ):

        years = months // 12

        remaining = months % 12

        if years and remaining:

            return (
                f"{years} years "
                f"{remaining} months"
            )

        if years:

            return f"{years} years"

        return f"{remaining} months"

    # =========================================================
    # EDUCATION
    # =========================================================

    def _education(self):

        records = self._credential_queryset(
            CredentialRecord.RecordType.EDUCATION
        )

        return [
            self._credential_data(record)
            for record in records
        ]

    # =========================================================
    # CERTIFICATIONS
    # =========================================================

    def _certifications(self):

        records = self._credential_queryset(
            CredentialRecord.RecordType.CERTIFICATION
        )

        records.sort(
            key=lambda record: (
                not self._is_current_credential(
                    record
                ),
                record.expiry_date
                or date.max,
            )
        )

        return [
            self._credential_data(record)
            for record in records
        ]

    # =========================================================
    # TRAINING
    # =========================================================

    def _training(self):

        if not self._template_requests(
            "training"
        ):

            return []

        records = self._credential_queryset(
            CredentialRecord.RecordType.TRAINING
        )

        return [
            self._credential_data(record)
            for record in records
        ]

    # =========================================================
    # CREDENTIAL QUERY
    # =========================================================

    def _credential_queryset(
        self,
        record_type,
    ):

        return list(
            CredentialRecord.objects
            .filter(
                professional=self.professional,
                record_type=record_type,
            )
            .exclude(
                status__in=[
                    CredentialRecord.Status.DRAFT,
                    CredentialRecord.Status.REVOKED,
                    CredentialRecord.Status.ARCHIVED,
                ]
            )
            .order_by(
                "-issue_date",
                "-created_at",
            )
        )

    # =========================================================
    # CREDENTIAL DATA
    # =========================================================

    def _credential_data(
        self,
        record,
    ):

        issuer = (
            record.issuing_organization_other
            or record.issuing_body_snapshot
            or (
                str(
                    record.issuing_organization
                )
                if record.issuing_organization
                else ""
            )
        )

        return {

            "id": record.id,

            "record_type": (
                record.record_type
            ),

            "title": record.title,

            "issuing_organization": issuer,

            "issuing_country_code": (
                record.issuing_country_code
            ),

            "discipline_or_field": (
                record.discipline_or_field
            ),

            "level_or_grade": (
                record.level_or_grade
            ),

            "issue_date": (
                record.issue_date.isoformat()
                if record.issue_date
                else None
            ),

            "expiry_date": (
                record.expiry_date.isoformat()
                if record.expiry_date
                else None
            ),

            "status": record.status,

            "verification_status": (
                record.verification_status
            ),

            "details": (
                record.details or {}
            ),
        }

    # =========================================================
    # CURRENT CREDENTIAL
    # =========================================================

    def _is_current_credential(
        self,
        record,
    ):

        if record.status in [
            CredentialRecord.Status.EXPIRED,
            CredentialRecord.Status.REVOKED,
            CredentialRecord.Status.ARCHIVED,
        ]:

            return False

        if record.expiry_date:

            return (
                record.expiry_date
                >= date.today()
            )

        return True

    # =========================================================
    # EMPLOYMENT
    # =========================================================

    def _employment(self):

        records = (
            EmploymentRecord.objects
            .filter(
                professional=self.professional
            )
            .order_by("-start_date")
        )

        result = []

        for record in records:

            if not self._resume_visible(
                getattr(
                    record,
                    "resume_visibility",
                    None,
                )
            ):

                continue

            result.append({

                "id": record.id,

                "employer": (
                    record.employer_name_snapshot
                    or record.employer_organization
                    or ""
                ),

                "job_title": (
                    record.job_title
                ),

                "employment_type": (
                    self._reference_value(
                        record.employment_type
                    )
                ),

                "country_code": (
                    record.country_code
                ),

                "city": record.city,

                "start_date": (
                    record.start_date.isoformat()
                    if record.start_date
                    else None
                ),

                "end_date": (
                    record.end_date.isoformat()
                    if record.end_date
                    else None
                ),

                "is_current": (
                    record.is_current
                ),

                "duties": (
                    record.duties
                ),

                "verification_status": (
                    record.verification_status
                ),
            })

        return result

    # =========================================================
    # PROJECTS
    # =========================================================

    def _projects(self):

        projects = (
            ProjectRecord.objects
            .filter(
                professional=self.professional
            )
            .prefetch_related(
                "project_scopes__scope_responses__form_field",
                "project_scopes__scope",
            )
            .order_by("-start_date")
        )

        result = []

        for project in projects:

            project_data = {

                "id": project.id,

                "project_name": (
                    project.project_name
                ),

                "employer": (
                    project.employer_organization
                    or ""
                ),

                "role_title": (
                    self._reference_value(
                        project.role_title
                    )
                ),

                "country_code": (
                    project.country_code
                ),

                "city": project.city,

                "start_date": (
                    project.start_date.isoformat()
                    if project.start_date
                    else None
                ),

                "end_date": (
                    project.end_date.isoformat()
                    if project.end_date
                    else None
                ),

                "is_current": (
                    project.is_current
                ),

                "allocation_percent": (
                    str(
                        project.allocation_percent
                    )
                    if project.allocation_percent
                    is not None
                    else None
                ),

                "working_arrangement": (
                    project.working_arrangement
                ),

                "engagement_explanation": (
                    project.engagement_explanation
                ),

                "responsibilities": (
                    project.responsibilities
                ),

                "achievements": (
                    project.achievements
                ),

                "standards_applied": (
                    project.standards_applied
                    or []
                ),

                "verification_status": (
                    project.verification_status
                ),

                "verified_field_days": (
                    str(
                        project.verified_field_days
                    )
                    if project.verified_field_days
                    is not None
                    else "0"
                ),

                "scopes": [],
            }

            # -------------------------------------------------
            # CLIENT VISIBILITY
            # -------------------------------------------------

            visibility = (
                project.client_visibility
            )

            if (
                visibility
                == ProjectRecord
                .ClientVisibility
                .SHOW_CLIENT_NAME
            ):

                project_data["client_name"] = (
                    project.client_name_snapshot
                    or project.client_organization
                    or ""
                )

            elif (
                visibility
                == ProjectRecord
                .ClientVisibility
                .SHOW_MASKED_CLIENT_CATEGORY
            ):

                project_data["client_name"] = (
                    "Confidential Client"
                )

            # CONFIDENTIAL_DO_NOT_DISPLAY
            # intentionally does not expose client name.

            # -------------------------------------------------
            # PROJECT SCOPES
            # -------------------------------------------------

            for project_scope in (
                project.project_scopes.all()
            ):

                if self.scope_ids:

                    if str(
                        project_scope.scope_id
                    ) not in [
                        str(scope_id)
                        for scope_id
                        in self.scope_ids
                    ]:

                        continue

                scope_data = {

                    "scope_id": (
                        project_scope.scope_id
                    ),

                    "scope_code": getattr(
                        project_scope.scope,
                        "code",
                        "",
                    ),

                    "scope_name": getattr(
                        project_scope.scope,
                        "scope_name",
                        "",
                    ),

                    "activity_summary": (
                        project_scope
                        .activity_summary
                    ),

                    "authority_action": (
                        self._reference_value(
                            project_scope
                            .authority_action
                        )
                    ),

                    "verification_status": (
                        project_scope
                        .verification_status
                    ),

                    "dynamic_fields": (
                        self._dynamic_scope_fields(
                            project_scope
                        )
                    ),
                }

                project_data[
                    "scopes"
                ].append(
                    scope_data
                )

            result.append(
                project_data
            )

        return result

    # =========================================================
    # DYNAMIC SCOPE FIELDS
    # =========================================================

    def _dynamic_scope_fields(
        self,
        project_scope,
    ):

        responses = (
            ScopeResponse.objects
            .filter(
                project_scope=project_scope
            )
            .select_related(
                "form_field",
                "form_field__form_module",
            )
            .order_by(
                "form_field__sequence",
                "repeat_index",
            )
        )

        result = []

        for response in responses:

            field = response.form_field

            if not field.is_active:
                continue

            value = response.value

            if value in [
                None,
                "",
                [],
                {},
            ]:

                continue

            visibility = (
                field.default_resume_visibility
            )

            visibility_value = str(
                visibility
            ).upper()

            # -------------------------------------------------
            # NEVER
            # -------------------------------------------------

            if visibility_value == "NEVER":
                continue

            # -------------------------------------------------
            # CLIENT SPECIFIC
            # -------------------------------------------------

            if (
                visibility_value
                == "CLIENT_SPECIFIC"
            ):

                if not self.template:
                    continue

                if not field.resume_token:
                    continue

                if not self._template_requests(
                    field.resume_token
                ):

                    continue

            result.append({

                "field_id": field.id,

                "field_code": (
                    field.field_code
                ),

                "field_label": (
                    field.field_label
                ),

                "resume_token": (
                    field.resume_token
                ),

                "data_type": (
                    field.data_type
                ),

                "repeatable": (
                    field.is_repeatable
                ),

                "repeat_group_key": (
                    str(
                        response
                        .repeat_group_key
                    )
                ),

                "repeat_index": (
                    response.repeat_index
                ),

                "value": value,

                "verification_status": (
                    response.verification_status
                ),
            })

        return result

    # =========================================================
    # SCOPE EXPERTISE
    # =========================================================

    def _scope_expertise(self):

        scopes = {}

        queryset = (
            ProjectScope.objects
            .filter(
                project__professional=self.professional
            )
            .select_related("scope")
        )

        if self.scope_ids:

            queryset = queryset.filter(
                scope_id__in=self.scope_ids
            )

        for project_scope in queryset:

            scope = project_scope.scope

            scope_id = scope.id

            if scope_id not in scopes:

                scopes[scope_id] = {

                    "scope_id": scope.id,

                    "scope_code": getattr(
                        scope,
                        "code",
                        "",
                    ),

                    "scope_name": getattr(
                        scope,
                        "scope_name",
                        "",
                    ),

                    "description": getattr(
                        scope,
                        "description",
                        "",
                    ),

                    "competency_focus": getattr(
                        scope,
                        "competency_focus",
                        "",
                    ),

                    "calendar_months": (
                        self._scope_calendar_months(
                            scope.id
                        )
                    ),

                    "verified_field_days": (
                        self._verified_field_days(
                            scope.id
                        )
                    ),
                }

        return list(
            scopes.values()
        )

    # =========================================================
    # SCOPE CALENDAR MONTHS
    # =========================================================

    def _scope_calendar_months(
        self,
        scope_id,
    ):

        project_scopes = (
            ProjectScope.objects
            .filter(
                scope_id=scope_id,
                project__professional=(
                    self.professional
                ),
            )
            .select_related("project")
        )

        intervals = []

        for project_scope in project_scopes:

            project = project_scope.project

            start = project.start_date

            end = (
                project.end_date
                or date.today()
            )

            if (
                start
                and end
                and start <= end
            ):

                intervals.append(
                    (start, end)
                )

        merged = self._merge_intervals(
            intervals
        )

        total_days = 0

        for start, end in merged:

            total_days += (
                end - start
            ).days + 1

        return round(
            total_days / 30.4375
        )

    # =========================================================
    # VERIFIED FIELD DAYS
    # =========================================================

    def _verified_field_days(
        self,
        scope_id,
    ):

        logs = (
            ExposureLog.objects
            .filter(
                professional=self.professional,
                project_scope__scope_id=scope_id,
                status=ExposureLog.Status.APPROVED,
            )
            .values(
                "activity_date",
                "day_fraction",
            )
            .order_by(
                "activity_date"
            )
        )

        daily = {}

        for log in logs:

            activity_date = (
                log["activity_date"]
            )

            fraction = (
                log["day_fraction"]
                or Decimal("0")
            )

            if activity_date not in daily:
                daily[activity_date] = (
                    Decimal("0")
                )

            daily[activity_date] = min(
                Decimal("1.00"),
                (
                    daily[activity_date]
                    + fraction
                )
            )

        total = sum(
            daily.values(),
            Decimal("0")
        )

        return float(total)

    # =========================================================
    # MERGE DATE INTERVALS
    # =========================================================

    def _merge_intervals(
        self,
        intervals,
    ):

        if not intervals:
            return []

        intervals = sorted(
            intervals,
            key=lambda x: x[0]
        )

        merged = [
            intervals[0]
        ]

        for current_start, current_end in (
            intervals[1:]
        ):

            previous_start, previous_end = (
                merged[-1]
            )

            if current_start <= (
                previous_end
            ):

                merged[-1] = (
                    previous_start,
                    max(
                        previous_end,
                        current_end,
                    ),
                )

            else:

                merged.append(
                    (
                        current_start,
                        current_end,
                    )
                )

        return merged

    # =========================================================
    # SKILLS
    # =========================================================

    def _skills(self):

        standards = []

        projects = (
            ProjectRecord.objects
            .filter(
                professional=self.professional
            )
        )

        for project in projects:

            for standard in (
                project.standards_applied
                or []
            ):

                if standard not in standards:

                    standards.append(
                        standard
                    )

        return {
            "codes_and_standards": standards
        }

    # =========================================================
    # LANGUAGES
    # =========================================================

    def _languages(self):

        # No language model was supplied.
        return []

    # =========================================================
    # REFERENCES
    # =========================================================

    def _references(self):

        if self._template_requests(
            "references"
        ):

            return {
                "items": [],
                "fallback": (
                    "Available upon request"
                ),
            }

        return []

    # =========================================================
    # CLIENT APPROVALS
    # =========================================================

    def _client_approvals(self):

        if not self._template_requests(
            "client_approval"
        ):

            return []

        records = self._credential_queryset(
            CredentialRecord.RecordType.CLIENT_APPROVAL
        )

        return [
            self._credential_data(record)
            for record in records
        ]

    # =========================================================
    # DECLARATION
    # =========================================================

    def _declaration(self):

        if not self._template_requests(
            "declaration"
        ):

            return None

        accuracy_consent = self._has_consent(
            ConsentRecord.ConsentType.PROFILE_ACCURACY
        )

        if not accuracy_consent:
            return None

        return {

            "text": (
                "I declare that the information "
                "provided in this resume is accurate "
                "to the best of my knowledge."
            ),

            "profile_accuracy_consent": True,
        }

    # =========================================================
    # REFERENCE VALUE
    # =========================================================

    def _reference_value(
        self,
        value,
    ):

        if not value:
            return None

        return {

            "id": value.id,

            "code": getattr(
                value,
                "code",
                "",
            ),

            "label": getattr(
                value,
                "label",
                str(value),
            ),
        }

    # =========================================================
    # RESUME VISIBILITY
    # =========================================================

    def _resume_visible(
        self,
        visibility,
    ):

        if not visibility:
            return True

        value = str(
            visibility
        ).upper()

        if value == "NEVER":
            return False

        return True