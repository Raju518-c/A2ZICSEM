"""catalog: platform-managed industries, levels, scopes, reusable scope
form modules and the 404 configurable scope fields.

Ownership and access: Platform Super Admin only. Tenant Admin has
read-only access and cannot create or alter industries, scopes, modules,
fields or Qualion levels.

None of these tables carry tenant_id — they are platform-level masters
shared by every tenant.
"""

from django.conf import settings
from django.db import models
from django.db.models import F, Q
from pydantic import ValidationError

from core.choices import DataClassification, PublicationStatus, ResumeVisibility
from core.models import CreatedOnlyModel, TimeStampedModel
from django.core.exceptions import ValidationError

class ReferencevalueoptionSet(models.Model):
    option_type=models.CharField(
        max_length=80, null=True, blank=True, help_text="Category of controlled value, e.g. INDUSTRY, QUALION_LEVEL, "
        "AUTHORITY_STATUS, CAREER_STAGE, QUALIFICATION_LEVEL, "
        "PROFESSIONAL_ROLE, STANDARD, EQUIPMENT, SOFTWARE.",
    )

class ReferenceValue(TimeStampedModel):
    """Single platform master for controlled values such as Industry,
    Qualion Level, Authority Status, Career Stage, Qualification Level,
    Standards, Equipment and Software.

    Key rules: Platform-level table with no tenant_id. Business tables
    reference the row ID, not a non-unique text code. Used only for values
    that require controlled matching/reporting.
    """    
    option_set = models.ForeignKey('ReferencevalueoptionSet', on_delete=models.PROTECT, null=True, blank=True,
        related_name='reference_values', help_text='Category of controlled value, e.g. INDUSTRY, QUALION_LEVEL, AUTHORITY_STATUS, CAREER_STAGE, QUALIFICATION_LEVEL, PROFESSIONAL_ROLE, STANDARD, EQUIPMENT, SOFTWARE.'
    )
    code = models.CharField(
        max_length=80, help_text="Stable uppercase machine code; unique with option_set."
    )
    label = models.CharField(max_length=160, help_text="User-facing display value.")
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
        help_text="Supports dependent values. Parent must be from the same "
        "or compatible option set; no cycles.",
    )
    sort_order = models.PositiveSmallIntegerField(default=0, help_text="Display order.")
    is_system = models.BooleanField(
        default=True, help_text="Marks protected platform baseline value."
    )
    is_active = models.BooleanField(
        default=True, help_text="Inactive values remain for historical references."
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional master configuration; schema depends on option_set.",
    )
    created_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        related_name="reference_values_created",
        help_text="Creator; Platform Super Admin only.",
    )
        
    def clean(self):
        if self.parent_id and self.parent_id == self.id:
            raise ValidationError(
                {"parent": "Parent cannot reference itself."}
            )      

    class Meta:
        db_table = "catalog_reference_value"
        verbose_name = "Reference Value"
        verbose_name_plural = "Reference Values"
        ordering = ["option_set", "sort_order", "label"]
        constraints = [
            models.UniqueConstraint(
                fields=["option_set", "code"], name="uniq_reference_value_option_set_code"
            ),            
        ]
    
  

    def __str__(self):
        return f"{self.option_set}:{self.code}"


class ScopeCatalog(TimeStampedModel):
    """Stores the global Industry + Survey/Inspection Scope combinations.
    The client blueprint currently defines 40 scope combinations.

    Key rules: Platform-level and Super Admin-managed. Published codes
    remain stable. A scope belongs to one industry and may load several
    reusable form modules.
    """

    code = models.CharField(
        max_length=40, unique=True, help_text="Globally unique stable code, e.g. OG-LPM."
    )
    industry = models.ForeignKey(
        ReferenceValue,
        on_delete=models.PROTECT,
        related_name="scopes",
        db_index=True,
        help_text="Industry to which the scope belongs. option_set must be INDUSTRY.",
    )
    scope_name = models.CharField(
        max_length=180,
        help_text="Survey or inspection scope name; unique with industry "
        "among active scopes.",
    )
    description = models.TextField(max_length=3000, blank=True, help_text="Scope description.")
    competency_focus = models.TextField(
        max_length=3000, blank=True, help_text="Competency direction for the scope."
    )
    suggested_resume_section = models.CharField(
        max_length=160, blank=True, help_text="Recommended resume section title (template hint only)."
    )
    activation_rule = models.JSONField(
        default=dict,
        blank=True,
        help_text="Optional rules controlling scope/module activation.",
    )
    version = models.PositiveIntegerField(
        default=1, help_text="Scope definition version; increment for material published changes."
    )
    status = models.CharField(
        max_length=20,
        choices=PublicationStatus.choices,
        default=PublicationStatus.DRAFT,
        db_index=True,
        help_text="Publication status.",
    )
    is_active = models.BooleanField(
        default=True, help_text="Selection availability; retired scopes remain readable."
    )
    created_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        related_name="scope_catalogs_created",
        help_text="Creator; Platform Super Admin only.",
    )

    class Meta:
        db_table = "catalog_scope_catalog"
        verbose_name = "Scope Catalog"
        verbose_name_plural = "Scope Catalogs"
        ordering = ["industry", "scope_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["industry", "scope_name"],
                condition=Q(is_active=True),
                name="uniq_scope_catalog_industry_scope_name_active",
            ),
        ]

    def __str__(self):
        return f"{self.code} — {self.scope_name}"


class FormModule(TimeStampedModel):
    """Stores reusable technical form sections such as Welding, NDT,
    Coating, HSE, Line Pipe and Marine Warranty Survey.

    Key rules: Platform-level and Super Admin-managed. Published versions
    are immutable; changes create a new version.
    """

    module_code = models.CharField(
        max_length=40, help_text="Stable code, e.g. SM-WELD; unique with version."
    )
    module_name = models.CharField(max_length=180, help_text="Module display name.")
    version = models.PositiveIntegerField(
        default=1, help_text="Module version; unique with module_code."
    )
    description = models.TextField(
        max_length=3000, blank=True, help_text="Purpose and scope of the module."
    )
    status = models.CharField(
        max_length=20,
        choices=PublicationStatus.choices,
        default=PublicationStatus.DRAFT,
        db_index=True,
        help_text="Publication status.",
    )
    effective_from = models.DateField(
        null=True, blank=True, help_text="Effective date; cannot be after retired date."
    )
    published_at = models.DateTimeField(
        null=True, blank=True, help_text="Publication timestamp; required when PUBLISHED."
    )
    retired_at = models.DateTimeField(
        null=True, blank=True, help_text="Retirement timestamp; required when retired."
    )
    created_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        related_name="form_modules_created",
        help_text="Creator; Platform Super Admin only.",
    )

    class Meta:
        db_table = "catalog_form_module"
        verbose_name = "Form Module"
        verbose_name_plural = "Form Modules"
        ordering = ["module_code", "version"]
        constraints = [
            models.UniqueConstraint(
                fields=["module_code", "version"], name="uniq_form_module_code_version"
            ),
            models.CheckConstraint(
                check=(~Q(status="PUBLISHED") | Q(published_at__isnull=False)),
                name="chk_form_module_published_at_required",
            ),
            models.CheckConstraint(
                check=(~Q(status="RETIRED") | Q(retired_at__isnull=False)),
                name="chk_form_module_retired_at_required",
            ),
        ]

    def __str__(self):
        return f"{self.module_code} v{self.version}"


class ScopeModule(CreatedOnlyModel):
    """Many-to-many mapping that defines which reusable form modules load
    for a selected Scope and in what order.

    Key rules: Platform-level and Super Admin-managed. One scope can have
    many modules and one module can be reused by many scopes.
    """

    scope = models.ForeignKey(
        ScopeCatalog,
        on_delete=models.CASCADE,
        related_name="scope_modules",
        db_index=True,
        help_text="Scope being configured; must be active or draft during configuration.",
    )
    form_module = models.ForeignKey(
        FormModule,
        on_delete=models.PROTECT,
        related_name="scope_modules",
        db_index=True,
        help_text="Reusable module assigned to the scope; published scope may "
        "use only a published module version.",
    )
    sequence = models.PositiveSmallIntegerField(
        default=0, help_text="Module display order; unique rendering sequence within scope."
    )
    is_required = models.BooleanField(
        default=True, help_text="Required modules cannot be skipped at scope submission."
    )
    activation_rule = models.JSONField(
        default=dict, blank=True, help_text="Optional conditional loading rule."
    )
    effective_from = models.DateField(
        null=True, blank=True, help_text="Mapping start date; cannot be after effective_to."
    )
    effective_to = models.DateField(
        null=True, blank=True, help_text="Mapping end date; must be on/after effective_from."
    )
    created_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        related_name="scope_modules_created",
        help_text="Creator; Platform Super Admin only.",
    )

    class Meta:
        db_table = "catalog_scope_module"
        verbose_name = "Scope Module"
        verbose_name_plural = "Scope Modules"
        ordering = ["scope", "sequence"]
        constraints = [
            models.UniqueConstraint(
                fields=["scope", "sequence"], name="uniq_scope_module_scope_sequence"
            ),
            models.CheckConstraint(
                check=(
                    Q(effective_from__isnull=True)
                    | Q(effective_to__isnull=True)
                    | Q(effective_from__lte=F("effective_to"))
                ),
                name="chk_scope_module_effective_from_before_to",
            ),
        ]

    def __str__(self):
        return f"{self.scope} → {self.form_module} (#{self.sequence})"


class FormField(TimeStampedModel):
    """Defines each dynamic question inside a FormModule. The 404
    client-provided scope fields are stored as rows here, not as 404
    database columns.

    Key rules: Platform-level and Super Admin-managed. Published field
    definitions are immutable. Validation schema must match data type.
    """

    class DataType(models.TextChoices):
        STRING = "STRING", "String"
        INTEGER = "INTEGER", "Integer"
        DECIMAL = "DECIMAL", "Decimal"
        DATE = "DATE", "Date"
        BOOLEAN = "BOOLEAN", "Boolean"
        ENUM = "ENUM", "Enum"
        ENUM_LIST = "ENUM_LIST", "Enum list"
        STRING_LIST = "STRING_LIST", "String list"
        RICH_TEXT = "RICH_TEXT", "Rich text"
        FILE = "FILE", "File"

    form_module = models.ForeignKey(
        FormModule,
        on_delete=models.CASCADE,
        related_name="fields",
        db_index=True,
        help_text="Owning form module; field belongs to one module version.",
    )
    field_code = models.CharField(
        max_length=140, help_text="Stable machine path; unique within form_module."
    )
    field_label = models.CharField(max_length=220, help_text="Question label.")
    purpose = models.CharField(
        max_length=300, blank=True, help_text="Short explanation of why the field is collected."
    )
    data_type = models.CharField(
        max_length=30, choices=DataType.choices, help_text="Expected answer type."
    )
    ui_control = models.CharField(
        max_length=50,
        help_text="Frontend input control from the allowed control list "
        "(text, textarea, select, multiselect, date, checkbox, number, file, etc).",
    )
    is_required = models.BooleanField(
        default=False, help_text="Enforced at module/project-scope submission."
    )
    is_repeatable = models.BooleanField(
        default=False,
        help_text="Whether multiple answer groups are allowed; repeatable "
        "fields use repeat group/index in ScopeResponse.",
    )
    option_set = models.CharField(
        max_length=80,
        blank=True,
        help_text="Controlled option set name; required for master-driven "
        "enum values, must match ReferenceValue.option_set.",
    )
    options_schema = models.JSONField(
        default=dict,
        blank=True,
        help_text="Inline/dependent option configuration; required for "
        "inline enum/list values.",
    )
    validation_schema = models.JSONField(
        default=dict,
        blank=True,
        help_text="Answer validation rules; must be compatible with data_type.",
    )
    evidence_rule = models.JSONField(
        default=dict, blank=True, help_text="Expected supporting evidence."
    )
    resume_token = models.CharField(
        max_length=180,
        blank=True,
        help_text="Token available to resume mapping; unique where populated.",
    )
    default_resume_visibility = models.CharField(
        max_length=30,
        choices=ResumeVisibility.choices,
        default=ResumeVisibility.OPTIONAL,
        help_text="Default resume display rule.",
    )
    data_classification = models.CharField(
        max_length=30,
        choices=DataClassification.choices,
        default=DataClassification.PROFESSIONAL,
        help_text="Data sensitivity level.",
    )
    sequence = models.PositiveIntegerField(
        default=0, help_text="Field display order; unique sequence recommended within module."
    )
    is_active = models.BooleanField(
        default=True, help_text="Selection/display status; inactive fields remain "
        "readable for historical responses."
    )
    created_by = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.PROTECT,
        related_name="form_fields_created",
        help_text="Creator; Platform Super Admin only.",
    )

    class Meta:
        db_table = "catalog_form_field"
        verbose_name = "Form Field"
        verbose_name_plural = "Form Fields"
        ordering = ["form_module", "sequence"]
        constraints = [
            models.UniqueConstraint(
                fields=["form_module", "field_code"], name="uniq_form_field_module_code"
            ),
            models.UniqueConstraint(
                fields=["resume_token"],
                condition=~Q(resume_token=""),
                name="uniq_form_field_resume_token",
            ),
        ]

    def __str__(self):
        return f"{self.form_module} — {self.field_code}"
