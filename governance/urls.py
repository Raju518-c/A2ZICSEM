from django.urls import path
from .views import *

app_name = "governance"

urlpatterns = [
    path(
        "audit-events/",
        AuditEventListCreateAPIView.as_view(),
        name="audit-event-list-create",
    ),

    path(
        "audit-events/<int:pk>/",
        AuditEventRetrieveUpdateDeleteAPIView.as_view(),
        name="audit-event-detail",
    ),
    
    path(
        "calculated-field-overrides/",
        CalculatedFieldOverrideListCreateAPIView.as_view(),
        name="calculated-field-override-list-create",
    ),

    path(
        "calculated-field-overrides/<int:pk>/",
        CalculatedFieldOverrideRetrieveUpdateDeleteAPIView.as_view(),
        name="calculated-field-override-detail",
    ),

    # CalculatedFieldValueHistory

    path(
        "calculated-field-value-history/",
        CalculatedFieldValueHistoryListCreateAPIView.as_view(),
        name="calculated-field-value-history-list-create",
    ),

    path(
        "calculated-field-value-history/<int:pk>/",
        CalculatedFieldValueHistoryRetrieveUpdateDeleteAPIView.as_view(),
        name="calculated-field-value-history-detail",
    ),

    # CalculationRuleSet

    path(
        "calculation-rule-sets/",
        CalculationRuleSetListCreateAPIView.as_view(),
        name="calculation-rule-set-list-create",
    ),

    path(
        "calculation-rule-sets/<int:pk>/",
        CalculationRuleSetRetrieveUpdateDeleteAPIView.as_view(),
        name="calculation-rule-set-detail",
    ),

    # CalculationRule

    path(
        "calculation-rules/",
        CalculationRuleListCreateAPIView.as_view(),
        name="calculation-rule-list-create",
    ),

    path(
        "calculation-rules/<int:pk>/",
        CalculationRuleRetrieveUpdateDeleteAPIView.as_view(),
        name="calculation-rule-detail",
    ),
    
    path(
        "calculated-fields/calculate/",
        CalculateSystemFieldAPIView.as_view(),
        name="calculated-field-calculate",
    ),
    path(
        "calculated-fields/override/",
        OverrideCalculatedFieldAPIView.as_view(),
        name="calculated-field-override",
    ),
]
