"""Phase 2 master-rule ownership and tenant rule selection.

Import these classes at the END of governance/models.py (or keep this module and
import its models there). They preserve legacy CalculationRule records.
"""
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, F
from django.utils import timezone
from core.models import TimeStampedModel


class MasterCalculationRuleSet(TimeStampedModel):
    """One immutable-on-publication SuperAdmin-authored version of a policy.

    Child CalculationRule rows are connected via master_rule_set. A QUALION_LEVEL
    set normally contains one CalculationRule with L0-L5 QualionLevelConditions.
    """
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        IN_REVIEW = 'IN_REVIEW', 'In review'
        PUBLISHED = 'PUBLISHED', 'Published'
        RETIRED = 'RETIRED', 'Retired'

    class TargetType(models.TextChoices):
        INDUSTRY = 'INDUSTRY', 'Industry (all scopes)'
        SCOPE = 'SCOPE', 'Specific scope'

    code = models.CharField(max_length=80)
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    calculation_field_code = models.CharField(max_length=50, choices=[
        ('QUALION_LEVEL','Qualion Level'),
        ('DEPLOYABILITY_FLAG','Deployability'),
        ('CANDIDATE_MENTOR_CLASSIFICATION','Classification'),
    ])
    target_type = models.CharField(max_length=10, choices=TargetType.choices)
    industry = models.ForeignKey('catalog.ReferenceValue', on_delete=models.PROTECT,
                                 null=True, blank=True, related_name='master_calculation_rule_sets')
    scope = models.ForeignKey('catalog.ScopeCatalog', on_delete=models.PROTECT,
                              null=True, blank=True, related_name='master_calculation_rule_sets')
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey('accounts.UserTbl', on_delete=models.PROTECT, related_name='master_rules_created')
    published_by = models.ForeignKey('accounts.UserTbl', on_delete=models.PROTECT,
                                     null=True, blank=True, related_name='master_rules_published')
    published_at = models.DateTimeField(null=True, blank=True)
    supersedes = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True,
                                   related_name='replacement_versions')
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'governance_master_calculation_rule_set'
        constraints = [
            models.UniqueConstraint(fields=['code','version'], name='uq_master_rule_code_version'),
            models.CheckConstraint(check=Q(effective_from__isnull=True) | Q(effective_to__isnull=True) |
                                   Q(effective_from__lte=F('effective_to')), name='chk_master_rule_dates'),
            models.CheckConstraint(check=~Q(status='PUBLISHED') |
                                   (Q(published_at__isnull=False) & Q(published_by__isnull=False)),
                                   name='chk_master_rule_publish_audit'),
        ]

    def clean(self):
        super().clean()
        if self.target_type == self.TargetType.INDUSTRY:
            if not self.industry_id or self.scope_id:
                raise ValidationError('Industry rules require industry and no scope.')
            if self.industry.option_set.option_type != 'INDUSTRY':
                raise ValidationError({'industry':'Must be INDUSTRY ReferenceValue.'})
        elif self.target_type == self.TargetType.SCOPE:
            if not self.scope_id or self.industry_id:
                raise ValidationError('Scope rules require scope and no industry.')
        if self.supersedes_id and self.supersedes_id == self.pk:
            raise ValidationError({'supersedes':'Cannot supersede itself.'})

    def covers_scope(self, scope):
        if self.target_type == self.TargetType.SCOPE:
            return self.scope_id == scope.pk
        return self.industry_id == scope.industry_id

    def __str__(self):
        return f'{self.code} v{self.version} - {self.calculation_field_code}'


class MasterRuleAuthorAssignment(TimeStampedModel):
    """SuperAdmin delegates authoring/review to an authorized platform mentor."""
    rule_set = models.ForeignKey(MasterCalculationRuleSet, on_delete=models.PROTECT, related_name='author_assignments')
    assigned_to = models.ForeignKey('accounts.UserTbl', on_delete=models.PROTECT, related_name='assigned_master_rule_work')
    assigned_by = models.ForeignKey('accounts.UserTbl', on_delete=models.PROTECT, related_name='delegated_master_rule_work')
    task = models.CharField(max_length=20, choices=[('AUTHOR','Author'),('REVIEW','Review')])
    status = models.CharField(max_length=20, choices=[('OPEN','Open'),('SUBMITTED','Submitted'),('CLOSED','Closed')], default='OPEN')
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'governance_master_rule_author_assignment'


class TenantRuleSelection(TimeStampedModel):
    """Tenant's selection of a published master policy for a target.

    A target may be an entire industry or one scope. Scope-specific selections
    override industry selections for that scope. Prevent duplicate active
    selections for identical targets in a service with select_for_update().
    """
    class TargetType(models.TextChoices):
        INDUSTRY = 'INDUSTRY', 'Industry'
        SCOPE = 'SCOPE', 'Scope'

    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.PROTECT, related_name='rule_selections')
    master_rule_set = models.ForeignKey(MasterCalculationRuleSet, on_delete=models.PROTECT,
                                        related_name='tenant_selections')
    calculation_field_code = models.CharField(max_length=50, choices=[
        ('QUALION_LEVEL','Qualion Level'),('DEPLOYABILITY_FLAG','Deployability'),
        ('CANDIDATE_MENTOR_CLASSIFICATION','Classification')])
    target_type = models.CharField(max_length=10, choices=TargetType.choices)
    industry = models.ForeignKey('catalog.ReferenceValue', on_delete=models.PROTECT,
                                 null=True, blank=True, related_name='tenant_rule_selections')
    scope = models.ForeignKey('catalog.ScopeCatalog', on_delete=models.PROTECT,
                              null=True, blank=True, related_name='tenant_rule_selections')
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    selected_by = models.ForeignKey('accounts.UserTbl', on_delete=models.PROTECT, related_name='rule_selections_made')
    selected_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'governance_tenant_rule_selection'
        indexes = [models.Index(fields=['tenant','calculation_field_code','is_active'])]
        constraints = [
            models.CheckConstraint(check=Q(effective_from__isnull=True) | Q(effective_to__isnull=True) |
                                   Q(effective_from__lte=F('effective_to')), name='chk_tenant_selection_dates'),
            models.UniqueConstraint(fields=['tenant','calculation_field_code','scope'],
                                    condition=Q(is_active=True, target_type='SCOPE'),
                                    name='uq_active_tenant_field_scope'),
            models.UniqueConstraint(fields=['tenant','calculation_field_code','industry'],
                                    condition=Q(is_active=True, target_type='INDUSTRY'),
                                    name='uq_active_tenant_field_industry'),
        ]

    def clean(self):
        super().clean()
        master = self.master_rule_set
        if master.status != MasterCalculationRuleSet.Status.PUBLISHED:
            raise ValidationError({'master_rule_set':'Only published master rule sets can be selected.'})
        if self.calculation_field_code != master.calculation_field_code:
            raise ValidationError({'calculation_field_code':'Must match master rule field.'})
        if self.target_type == self.TargetType.INDUSTRY:
            if not self.industry_id or self.scope_id:
                raise ValidationError('Industry selection needs industry only.')
            if master.target_type != MasterCalculationRuleSet.TargetType.INDUSTRY or master.industry_id != self.industry_id:
                raise ValidationError('Industry selection must match industry-wide master rule.')
        elif self.target_type == self.TargetType.SCOPE:
            if not self.scope_id or self.industry_id:
                raise ValidationError('Scope selection needs scope only.')
            if not master.covers_scope(self.scope):
                raise ValidationError('Master rule does not cover selected scope.')
        else:
            raise ValidationError('Invalid target type.')


def resolve_tenant_rule_selection(tenant, scope, field_code, on_date=None):
    """Read-only effective policy resolver, explicit scope override first."""
    on_date = on_date or timezone.localdate()
    base = TenantRuleSelection.objects.select_related('master_rule_set').filter(
        tenant=tenant, calculation_field_code=field_code, is_active=True,
        master_rule_set__status='PUBLISHED',
    ).filter(Q(effective_from__isnull=True) | Q(effective_from__lte=on_date)).filter(
        Q(effective_to__isnull=True) | Q(effective_to__gte=on_date))
    selected = base.filter(target_type='SCOPE', scope=scope).first()
    if selected:
        return selected
    return base.filter(target_type='INDUSTRY', industry_id=scope.industry_id).first()
