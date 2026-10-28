"""Promotion recommendations and decision history. Uses existing ProfessionalScope."""
from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from core.models import TimeStampedModel


class PromotionRecommendation(TimeStampedModel):
    class Status(models.TextChoices):
        RECOMMENDED = 'RECOMMENDED', 'Recommended'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        WITHDRAWN = 'WITHDRAWN', 'Withdrawn'

    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.PROTECT, related_name='promotion_recommendations')
    professional_scope = models.ForeignKey('competency.ProfessionalScope', on_delete=models.PROTECT,
                                           related_name='promotion_recommendations')
    rule_selection = models.ForeignKey('governance.TenantRuleSelection', on_delete=models.PROTECT,
                                       related_name='promotion_recommendations')
    from_level = models.ForeignKey('catalog.ReferenceValue', on_delete=models.PROTECT,
                                   related_name='promotions_from')
    to_level = models.ForeignKey('catalog.ReferenceValue', on_delete=models.PROTECT,
                                 related_name='promotions_to')
    eligibility_snapshot = models.JSONField(default=dict)
    mentor = models.ForeignKey('accounts.UserTbl', on_delete=models.PROTECT,
                               related_name='promotion_recommendations_authored')
    mentor_comments = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECOMMENDED)
    decided_by = models.ForeignKey('accounts.UserTbl', on_delete=models.PROTECT,
                                   null=True, blank=True, related_name='promotion_recommendations_decided')
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_reason = models.TextField(blank=True)

    class Meta:
        db_table = 'governance_promotion_recommendation'
        constraints = [
            models.UniqueConstraint(fields=['professional_scope'], condition=Q(status='RECOMMENDED'),
                                    name='uq_pending_promotion_per_scope'),
        ]

    def clean(self):
        super().clean()
        if self.rule_selection_id and self.rule_selection.tenant_id != self.tenant_id:
            raise ValidationError('Promotion rule selection must belong to tenant.')
        if self.rule_selection_id and self.rule_selection.calculation_field_code != 'QUALION_LEVEL':
            raise ValidationError('Promotion requires a Qualion Level rule selection.')
        if self.from_level_id and self.to_level_id:
            if self.from_level.option_set.option_type != 'QUALION_LEVEL' or self.to_level.option_set.option_type != 'QUALION_LEVEL':
                raise ValidationError('Both levels must be QUALION_LEVEL reference values.')
            if self.to_level.sort_order <= self.from_level.sort_order:
                raise ValidationError('Promotion target must be higher than current level.')


class PromotionLevelHistory(TimeStampedModel):
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.PROTECT)
    professional_scope = models.ForeignKey('competency.ProfessionalScope', on_delete=models.PROTECT,
                                           related_name='promotion_level_history')
    recommendation = models.OneToOneField(PromotionRecommendation, on_delete=models.PROTECT,
                                          related_name='level_history')
    from_level = models.ForeignKey('catalog.ReferenceValue', on_delete=models.PROTECT,
                                   related_name='promotion_history_from')
    to_level = models.ForeignKey('catalog.ReferenceValue', on_delete=models.PROTECT,
                                 related_name='promotion_history_to')
    approved_by = models.ForeignKey('accounts.UserTbl', on_delete=models.PROTECT)
    effective_at = models.DateTimeField()

    class Meta:
        db_table = 'governance_promotion_level_history'
