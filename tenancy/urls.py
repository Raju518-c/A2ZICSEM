from django.urls import path

from .views import *

app_name = "tenancy"

urlpatterns = [
    path(
        "tenants/combined/",
        TenantCombinedCreateAPIView.as_view(),
        name="tenant-combined-create",
    ),           
    path("tenants/", TenantListCreateAPIView.as_view(), name="tenant-list-create"),
    path(
        "tenants/<int:pk>/",
        TenantRetrieveUpdateDeleteAPIView.as_view(),
        name="tenant-detail",
    ),
    path(
        "tenant-operations/",
        TenantOperationListCreateAPIView.as_view(),
        name="tenant-operation-list-create",
    ),
    path(
        "tenant-operations/<int:pk>/",
        TenantOperationRetrieveUpdateDeleteAPIView.as_view(),
        name="tenant-operation-detail",
    ),
    path(
        "tenant-by-host/",
        TenantResolveByHostAPIView.as_view(),
        name="tenant-by-host",
    ),

    path(
        "organizations/",
        OrganizationListCreateAPIView.as_view(),
        name="organization-list-create",
    ),

    path(
        "organizations/<uuid:pk>/",
        OrganizationRetrieveUpdateDeleteAPIView.as_view(),
        name="organization-detail",
    ),    
    
    path(
        "tenant-legal-entities/",
        TenantLegalEntityListCreateAPIView.as_view(),
        name="tenant-legal-entity-list-create",
    ),
    path(
        "tenant-legal-entities/<uuid:public_id>/",
        TenantLegalEntityRetrieveUpdateDeleteAPIView.as_view(),
        name="tenant-legal-entity-detail",
    ),

    # TenantTaxRegistration
    path(
        "tenant-tax-registrations/",
        TenantTaxRegistrationListCreateAPIView.as_view(),
        name="tenant-tax-registration-list-create",
    ),
    path(
        "tenant-tax-registrations/<uuid:public_id>/",
        TenantTaxRegistrationRetrieveUpdateDeleteAPIView.as_view(),
        name="tenant-tax-registration-detail",
    ),

    # TenantDomain
    path(
        "tenant-domains/",
        TenantDomainListCreateAPIView.as_view(),
        name="tenant-domain-list-create",
    ),
    path(
        "tenant-domains/<uuid:public_id>/",
        TenantDomainRetrieveUpdateDeleteAPIView.as_view(),
        name="tenant-domain-detail",
    ),
    
    path("tenant-industries/", TenantIndustryListCreateAPIView.as_view(), name="tenant-industry-list-create"),
    path("tenant-industries/<uuid:public_id>/", TenantIndustryRetrieveUpdateDeleteAPIView.as_view(), name="tenant-industry-detail"),

    path("tenant-scopes/", TenantScopeListCreateAPIView.as_view(), name="tenant-scope-list-create"),
    path("tenant-scopes/<uuid:public_id>/", TenantScopeRetrieveUpdateDeleteAPIView.as_view(), name="tenant-scope-detail"),

    path("tenant-business-units/", TenantBusinessUnitListCreateAPIView.as_view(), name="tenant-business-unit-list-create"),
    path("tenant-business-units/<uuid:public_id>/", TenantBusinessUnitRetrieveUpdateDeleteAPIView.as_view(), name="tenant-business-unit-detail"),

    path("tenant-locations/", TenantLocationListCreateAPIView.as_view(), name="tenant-location-list-create"),
    path("tenant-locations/<uuid:public_id>/", TenantLocationRetrieveUpdateDeleteAPIView.as_view(), name="tenant-location-detail"),
    
    path("tenant-authorised-representatives/", TenantAuthorisedRepresentativeListCreateAPIView.as_view(), name="tenant-authorised-representative-list-create"),
    path("tenant-authorised-representatives/<uuid:public_id>/", TenantAuthorisedRepresentativeRetrieveUpdateDeleteAPIView.as_view(), name="tenant-authorised-representative-detail"),

    path("tenant-contacts/", TenantContactListCreateAPIView.as_view(), name="tenant-contact-list-create"),
    path("tenant-contacts/<uuid:public_id>/", TenantContactRetrieveUpdateDeleteAPIView.as_view(), name="tenant-contact-detail"),

    path("tenant-verifications/", TenantVerificationListCreateAPIView.as_view(), name="tenant-verification-list-create"),
    path("tenant-verifications/<int:pk>/", TenantVerificationRetrieveUpdateDeleteAPIView.as_view(), name="tenant-verification-detail"),

    path("tenant-documents/", TenantDocumentListCreateAPIView.as_view(), name="tenant-document-list-create"),
    path("tenant-documents/<uuid:public_id>/", TenantDocumentRetrieveUpdateDeleteAPIView.as_view(), name="tenant-document-detail"),
    
    
    path("tenant-legal-acceptances/", TenantLegalAcceptanceListCreateAPIView.as_view(), name="tenant-legal-acceptance-list-create"),
    path("tenant-legal-acceptances/<uuid:public_id>/", TenantLegalAcceptanceRetrieveAPIView.as_view(), name="tenant-legal-acceptance-detail"),

    path("tenant-legal-settings/", TenantLegalSettingsListCreateAPIView.as_view(), name="tenant-legal-settings-list-create"),
    path("tenant-legal-settings/<uuid:public_id>/", TenantLegalSettingsRetrieveUpdateDeleteAPIView.as_view(), name="tenant-legal-settings-detail"),

    path("tenant-ndas/", TenantNdaListCreateAPIView.as_view(), name="tenant-nda-list-create"),
    path("tenant-ndas/<uuid:public_id>/", TenantNdaRetrieveUpdateDeleteAPIView.as_view(), name="tenant-nda-detail"),

    path("tenant-settings/", TenantSettingsListCreateAPIView.as_view(), name="tenant-settings-list-create"),
    path("tenant-settings/<uuid:public_id>/", TenantSettingsRetrieveUpdateDeleteAPIView.as_view(), name="tenant-settings-detail"),
    
    path("tenant-subscriptions/", TenantSubscriptionListCreateAPIView.as_view(), name="tenant-subscription-list-create"),
    path("tenant-subscriptions/<uuid:public_id>/", TenantSubscriptionRetrieveAPIView.as_view(), name="tenant-subscription-detail"),

    path("modules/", ModuleListCreateAPIView.as_view(), name="module-list-create"),
    path("modules/<uuid:public_id>/", ModuleRetrieveUpdateDeleteAPIView.as_view(), name="module-detail"),

    path("tenant-module-entitlements/", TenantModuleEntitlementListCreateAPIView.as_view(), name="tenant-module-entitlement-list-create"),
    path("tenant-module-entitlements/<uuid:public_id>/", TenantModuleEntitlementRetrieveUpdateDeleteAPIView.as_view(), name="tenant-module-entitlement-detail"),
    
    
    
    path("tenant-brandings/", TenantBrandingListCreateAPIView.as_view(), name="tenant-branding-list-create"),
    path("tenant-brandings/<uuid:public_id>/", TenantBrandingRetrieveUpdateDeleteAPIView.as_view(), name="tenant-branding-detail"),

    path("tenant-report-templates/", TenantReportTemplateListCreateAPIView.as_view(), name="tenant-report-template-list-create"),
    path("tenant-report-templates/<uuid:public_id>/", TenantReportTemplateRetrieveUpdateDeleteAPIView.as_view(), name="tenant-report-template-detail"),
    
    path("tenant-security-settings/", TenantSecuritySettingsListCreateAPIView.as_view(), name="tenant-security-settings-list-create"),
    path("tenant-security-settings/<uuid:public_id>/", TenantSecuritySettingsRetrieveUpdateDeleteAPIView.as_view(), name="tenant-security-settings-detail"),

    path("tenant-ip-restrictions/", TenantIPRestrictionListCreateAPIView.as_view(), name="tenant-ip-restriction-list-create"),
    path("tenant-ip-restrictions/<uuid:public_id>/", TenantIPRestrictionRetrieveUpdateDeleteAPIView.as_view(), name="tenant-ip-restriction-detail"),

    path("tenant-integrations/", TenantIntegrationListCreateAPIView.as_view(), name="tenant-integration-list-create"),
    path("tenant-integrations/<uuid:public_id>/", TenantIntegrationRetrieveUpdateDeleteAPIView.as_view(), name="tenant-integration-detail"),

    path("tenant-billing/", TenantBillingListCreateAPIView.as_view(), name="tenant-billing-list-create"),
    path("tenant-billing/<uuid:public_id>/", TenantBillingRetrieveUpdateDeleteAPIView.as_view(), name="tenant-billing-detail"),
    
    
    path("tenant-invitations/", TenantInvitationListCreateAPIView.as_view(), name="tenant-invitation-list-create"),
    path("tenant-invitations/<uuid:public_id>/", TenantInvitationRetrieveUpdateDeleteAPIView.as_view(), name="tenant-invitation-detail"),

    path("tenant-workflows/", TenantWorkflowListCreateAPIView.as_view(), name="tenant-workflow-list-create"),
    path("tenant-workflows/<uuid:public_id>/", TenantWorkflowRetrieveUpdateDeleteAPIView.as_view(), name="tenant-workflow-detail"),

    path("tenant-workflow-steps/", TenantWorkflowStepListCreateAPIView.as_view(), name="tenant-workflow-step-list-create"),
    path("tenant-workflow-steps/<uuid:public_id>/", TenantWorkflowStepRetrieveUpdateDeleteAPIView.as_view(), name="tenant-workflow-step-detail"),

    path("tenant-operation-logs/", TenantOperationLogListCreateAPIView.as_view(), name="tenant-operation-log-list-create"),
    path("tenant-operation-logs/<uuid:public_id>/", TenantOperationLogRetrieveUpdateDeleteAPIView.as_view(), name="tenant-operation-log-detail"),
    
    
    path("tenant-terminology/", TenantTerminologyListCreateAPIView.as_view(), name="tenant-terminology-list-create"),
    path("tenant-terminology/<uuid:public_id>/", TenantTerminologyRetrieveUpdateDeleteAPIView.as_view(), name="tenant-terminology-detail"),

    path("tenant-numbering-configs/", TenantNumberingConfigListCreateAPIView.as_view(), name="tenant-numbering-config-list-create"),
    path("tenant-numbering-configs/<uuid:public_id>/", TenantNumberingConfigRetrieveUpdateDeleteAPIView.as_view(), name="tenant-numbering-config-detail"),

    path("tenant-approval-matrices/", TenantApprovalMatrixListCreateAPIView.as_view(), name="tenant-approval-matrix-list-create"),
    path("tenant-approval-matrices/<uuid:public_id>/", TenantApprovalMatrixRetrieveUpdateDeleteAPIView.as_view(), name="tenant-approval-matrix-detail"),

    path("tenant-notification-settings/", TenantNotificationSettingsListCreateAPIView.as_view(), name="tenant-notification-settings-list-create"),
    path("tenant-notification-settings/<uuid:public_id>/", TenantNotificationSettingsRetrieveUpdateDeleteAPIView.as_view(), name="tenant-notification-settings-detail"),

    path("coi-declarations/", ConflictOfInterestDeclarationListCreateAPIView.as_view(), name="coi-declaration-list-create"),
    path("coi-declarations/<uuid:public_id>/", ConflictOfInterestDeclarationRetrieveUpdateDeleteAPIView.as_view(), name="coi-declaration-detail"),

    path("data-export-requests/", DataExportRequestListCreateAPIView.as_view(), name="data-export-request-list-create"),
    path("data-export-requests/<uuid:public_id>/", DataExportRequestRetrieveUpdateDeleteAPIView.as_view(), name="data-export-request-detail"),
    
    path("projects/", ProjectListCreateAPIView.as_view(), name="project-list-create"),
    path("projects/<uuid:public_id>/", ProjectRetrieveUpdateDeleteAPIView.as_view(), name="project-detail"),

    path("project-requirements/", ProjectRequirementListCreateAPIView.as_view(), name="project-requirement-list-create"),
    path("project-requirements/<uuid:public_id>/", ProjectRequirementRetrieveUpdateDeleteAPIView.as_view(), name="project-requirement-detail"),

    path("project-requirement-scopes/", ProjectRequirementScopeListCreateAPIView.as_view(), name="project-requirement-scope-list-create"),
    path("project-requirement-scopes/<uuid:public_id>/", ProjectRequirementScopeRetrieveUpdateDeleteAPIView.as_view(), name="project-requirement-scope-detail"),

    path("project-candidates/", ProjectCandidateListCreateAPIView.as_view(), name="project-candidate-list-create"),
    path("project-candidates/<uuid:public_id>/", ProjectCandidateRetrieveUpdateDeleteAPIView.as_view(), name="project-candidate-detail"),

    path("disclosure-requests/", DisclosureRequestListCreateAPIView.as_view(), name="disclosure-request-list-create"),
    path("disclosure-requests/<uuid:public_id>/", DisclosureRequestRetrieveUpdateDeleteAPIView.as_view(), name="disclosure-request-detail"),

    path("candidate-consents/", CandidateConsentListCreateAPIView.as_view(), name="candidate-consent-list-create"),
    path("candidate-consents/<uuid:public_id>/", CandidateConsentRetrieveAPIView.as_view(), name="candidate-consent-detail"),

    path("project-placements/", ProjectPlacementListCreateAPIView.as_view(), name="project-placement-list-create"),
    path("project-placements/<uuid:public_id>/", ProjectPlacementRetrieveUpdateDeleteAPIView.as_view(), name="project-placement-detail"),

    path("project-scope-links/", ProjectScopeLinkListCreateAPIView.as_view(), name="project-scope-link-list-create"),
    path("project-scope-links/<uuid:public_id>/", ProjectScopeLinkRetrieveUpdateDeleteAPIView.as_view(), name="project-scope-link-detail"),
    
    
    
    
    
    
    
    
    
]
