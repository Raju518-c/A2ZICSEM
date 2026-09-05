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
        "organizations/<int:pk>/",
        OrganizationRetrieveUpdateDeleteAPIView.as_view(),
        name="organization-detail",
    ),    
    
    path(
        "tenant-legal-entities/",
        TenantLegalEntityListCreateAPIView.as_view(),
        name="tenant-legal-entity-list-create",
    ),
    path(
        "tenant-legal-entities/<int:pk>/",
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
        "tenant-tax-registrations/<int:pk>/",
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
        "tenant-domains/<int:pk>/",
        TenantDomainRetrieveUpdateDeleteAPIView.as_view(),
        name="tenant-domain-detail",
    ),
    
    path("tenant-locations/", TenantLocationListCreateAPIView.as_view(), name="tenant-location-list-create"),
    path("tenant-locations/<int:pk>/", TenantLocationRetrieveUpdateDeleteAPIView.as_view(), name="tenant-location-detail"),
    
    path("tenant-authorised-representatives/", TenantAuthorisedRepresentativeListCreateAPIView.as_view(), name="tenant-authorised-representative-list-create"),
    path("tenant-authorised-representatives/<int:pk>/", TenantAuthorisedRepresentativeRetrieveUpdateDeleteAPIView.as_view(), name="tenant-authorised-representative-detail"),

    path("tenant-contacts/", TenantContactListCreateAPIView.as_view(), name="tenant-contact-list-create"),
    path("tenant-contacts/<int:pk>/", TenantContactRetrieveUpdateDeleteAPIView.as_view(), name="tenant-contact-detail"),

    path("tenant-verifications/", TenantVerificationListCreateAPIView.as_view(), name="tenant-verification-list-create"),
    path("tenant-verifications/<int:pk>/", TenantVerificationRetrieveUpdateDeleteAPIView.as_view(), name="tenant-verification-detail"),

    path("tenants/<int:tenant_id>/submit/", TenantSubmitAPIView.as_view(), name="tenant-submit"),
    path("tenants/<int:tenant_id>/resubmit/", TenantResubmitAPIView.as_view(), name="tenant-resubmit"),
    path("tenants/<int:tenant_id>/review-decision/", TenantReviewDecisionAPIView.as_view(), name="tenant-review-decision"),
    path("tenants/<int:tenant_id>/stage1-details/", TenantStage1DetailsAPIView.as_view(), name="tenant-stage1-details"),

    path("tenant-documents/", TenantDocumentListCreateAPIView.as_view(), name="tenant-document-list-create"),
    path("tenant-documents/<int:pk>/", TenantDocumentRetrieveUpdateDeleteAPIView.as_view(), name="tenant-document-detail"),
    
    
    path("tenant-legal-acceptances/", TenantLegalAcceptanceListCreateAPIView.as_view(), name="tenant-legal-acceptance-list-create"),
    path("tenant-legal-acceptances/<int:pk>/", TenantLegalAcceptanceRetrieveAPIView.as_view(), name="tenant-legal-acceptance-detail"),

    path("tenant-legal-settings/", TenantLegalSettingsListCreateAPIView.as_view(), name="tenant-legal-settings-list-create"),
    path("tenant-legal-settings/<int:pk>/", TenantLegalSettingsRetrieveUpdateDeleteAPIView.as_view(), name="tenant-legal-settings-detail"),

    path("tenant-ndas/", TenantNdaListCreateAPIView.as_view(), name="tenant-nda-list-create"),
    path("tenant-ndas/<int:pk>/", TenantNdaRetrieveUpdateDeleteAPIView.as_view(), name="tenant-nda-detail"),

    path("tenant-settings/", TenantSettingsListCreateAPIView.as_view(), name="tenant-settings-list-create"),
    path("tenant-settings/<int:pk>/", TenantSettingsRetrieveUpdateDeleteAPIView.as_view(), name="tenant-settings-detail"),
    
    path("tenant-subscriptions/", TenantSubscriptionListCreateAPIView.as_view(), name="tenant-subscription-list-create"),
    path("tenant-subscriptions/<int:pk>/", TenantSubscriptionRetrieveAPIView.as_view(), name="tenant-subscription-detail"),

    path("modules/", ModuleListCreateAPIView.as_view(), name="module-list-create"),
    path("modules/<int:pk>/", ModuleRetrieveUpdateDeleteAPIView.as_view(), name="module-detail"),

    path("tenant-module-entitlements/", TenantModuleEntitlementListCreateAPIView.as_view(), name="tenant-module-entitlement-list-create"),
    path("tenant-module-entitlements/<int:pk>/", TenantModuleEntitlementRetrieveUpdateDeleteAPIView.as_view(), name="tenant-module-entitlement-detail"),
    
    
    
    path("tenant-brandings/", TenantBrandingListCreateAPIView.as_view(), name="tenant-branding-list-create"),
    path("tenant-brandings/<int:pk>/", TenantBrandingRetrieveUpdateDeleteAPIView.as_view(), name="tenant-branding-detail"),

    path("tenant-report-templates/", TenantReportTemplateListCreateAPIView.as_view(), name="tenant-report-template-list-create"),
    path("tenant-report-templates/<int:pk>/", TenantReportTemplateRetrieveUpdateDeleteAPIView.as_view(), name="tenant-report-template-detail"),
    
    path("tenant-security-settings/", TenantSecuritySettingsListCreateAPIView.as_view(), name="tenant-security-settings-list-create"),
    path("tenant-security-settings/<int:pk>/", TenantSecuritySettingsRetrieveUpdateDeleteAPIView.as_view(), name="tenant-security-settings-detail"),

    path("tenant-ip-restrictions/", TenantIPRestrictionListCreateAPIView.as_view(), name="tenant-ip-restriction-list-create"),
    path("tenant-ip-restrictions/<int:pk>/", TenantIPRestrictionRetrieveUpdateDeleteAPIView.as_view(), name="tenant-ip-restriction-detail"),

    path("tenant-integrations/", TenantIntegrationListCreateAPIView.as_view(), name="tenant-integration-list-create"),
    path("tenant-integrations/<int:pk>/", TenantIntegrationRetrieveUpdateDeleteAPIView.as_view(), name="tenant-integration-detail"),

    path("tenant-billing/", TenantBillingListCreateAPIView.as_view(), name="tenant-billing-list-create"),
    path("tenant-billing/<int:pk>/", TenantBillingRetrieveUpdateDeleteAPIView.as_view(), name="tenant-billing-detail"),
    
    
    path("tenant-invitations/", TenantInvitationListCreateAPIView.as_view(), name="tenant-invitation-list-create"),
    path("tenant-invitations/<int:pk>/", TenantInvitationRetrieveUpdateDeleteAPIView.as_view(), name="tenant-invitation-detail"),

    path("tenant-workflows/", TenantWorkflowListCreateAPIView.as_view(), name="tenant-workflow-list-create"),
    path("tenant-workflows/<int:pk>/", TenantWorkflowRetrieveUpdateDeleteAPIView.as_view(), name="tenant-workflow-detail"),

    path("tenant-workflow-steps/", TenantWorkflowStepListCreateAPIView.as_view(), name="tenant-workflow-step-list-create"),
    path("tenant-workflow-steps/<int:pk>/", TenantWorkflowStepRetrieveUpdateDeleteAPIView.as_view(), name="tenant-workflow-step-detail"),

    path("tenant-operation-logs/", TenantOperationLogListCreateAPIView.as_view(), name="tenant-operation-log-list-create"),
    path("tenant-operation-logs/<int:pk>/", TenantOperationLogRetrieveUpdateDeleteAPIView.as_view(), name="tenant-operation-log-detail"),
    
    
    path("tenant-terminology/", TenantTerminologyListCreateAPIView.as_view(), name="tenant-terminology-list-create"),
    path("tenant-terminology/<int:pk>/", TenantTerminologyRetrieveUpdateDeleteAPIView.as_view(), name="tenant-terminology-detail"),

    path("tenant-numbering-configs/", TenantNumberingConfigListCreateAPIView.as_view(), name="tenant-numbering-config-list-create"),
    path("tenant-numbering-configs/<int:pk>/", TenantNumberingConfigRetrieveUpdateDeleteAPIView.as_view(), name="tenant-numbering-config-detail"),

    path("tenant-approval-matrices/", TenantApprovalMatrixListCreateAPIView.as_view(), name="tenant-approval-matrix-list-create"),
    path("tenant-approval-matrices/<int:pk>/", TenantApprovalMatrixRetrieveUpdateDeleteAPIView.as_view(), name="tenant-approval-matrix-detail"),

    path("tenant-notification-settings/", TenantNotificationSettingsListCreateAPIView.as_view(), name="tenant-notification-settings-list-create"),
    path("tenant-notification-settings/<int:pk>/", TenantNotificationSettingsRetrieveUpdateDeleteAPIView.as_view(), name="tenant-notification-settings-detail"),

    path("coi-declarations/", ConflictOfInterestDeclarationListCreateAPIView.as_view(), name="coi-declaration-list-create"),
    path("coi-declarations/<int:pk>/", ConflictOfInterestDeclarationRetrieveUpdateDeleteAPIView.as_view(), name="coi-declaration-detail"),

    path("data-export-requests/", DataExportRequestListCreateAPIView.as_view(), name="data-export-request-list-create"),
    path("data-export-requests/<int:pk>/", DataExportRequestRetrieveUpdateDeleteAPIView.as_view(), name="data-export-request-detail"),
    
    path("projects/create-with-memberships/", ProjectCreateWithMembershipsAPIView.as_view(), name="project-create-with-memberships"),
    path("projects/", ProjectListCreateAPIView.as_view(), name="project-list-create"),
    path("projects/<int:pk>/", ProjectRetrieveUpdateDeleteAPIView.as_view(), name="project-detail"),

    path("project-memberships/", ProjectMembershipListCreateAPIView.as_view(), name="project-membership-list-create"),
    path("project-memberships/<int:pk>/", ProjectMembershipRetrieveUpdateDeleteAPIView.as_view(), name="project-membership-detail"),

    path("project-requirements/", ProjectRequirementListCreateAPIView.as_view(), name="project-requirement-list-create"),
    path("project-requirements/<int:pk>/", ProjectRequirementRetrieveUpdateDeleteAPIView.as_view(), name="project-requirement-detail"),

    path("project-requirement-scopes/", ProjectRequirementScopeListCreateAPIView.as_view(), name="project-requirement-scope-list-create"),
    path("project-requirement-scopes/<int:pk>/", ProjectRequirementScopeRetrieveUpdateDeleteAPIView.as_view(), name="project-requirement-scope-detail"),

    path("project-candidates/", ProjectCandidateListCreateAPIView.as_view(), name="project-candidate-list-create"),
    path("project-candidates/<int:pk>/", ProjectCandidateRetrieveUpdateDeleteAPIView.as_view(), name="project-candidate-detail"),

    path("disclosure-requests/", DisclosureRequestListCreateAPIView.as_view(), name="disclosure-request-list-create"),
    path("disclosure-requests/<int:pk>/", DisclosureRequestRetrieveUpdateDeleteAPIView.as_view(), name="disclosure-request-detail"),

    path("candidate-consents/", CandidateConsentListCreateAPIView.as_view(), name="candidate-consent-list-create"),
    path("candidate-consents/<int:pk>/", CandidateConsentRetrieveAPIView.as_view(), name="candidate-consent-detail"),

    path("project-placements/", ProjectPlacementListCreateAPIView.as_view(), name="project-placement-list-create"),
    path("project-placements/<int:pk>/", ProjectPlacementRetrieveUpdateDeleteAPIView.as_view(), name="project-placement-detail"),

    path("project-scope-links/", ProjectScopeLinkListCreateAPIView.as_view(), name="project-scope-link-list-create"),
    path("project-scope-links/<int:pk>/", ProjectScopeLinkRetrieveUpdateDeleteAPIView.as_view(), name="project-scope-link-detail"),
    
    
    
    
    
    
    
    
    
]
