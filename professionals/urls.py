from django.urls import path

from .views import (
    CapabilityRecordListCreateAPIView,
    CapabilityRecordRetrieveUpdateDeleteAPIView,
    ContactRecordListCreateAPIView,
    ContactRecordRetrieveUpdateDeleteAPIView,
    CredentialRecordListCreateAPIView,
    CredentialRecordRetrieveUpdateDeleteAPIView,
    ProfessionalProfileListCreateAPIView,
    ProfessionalProfileRetrieveUpdateDeleteAPIView,
    ProfessionalReviewListCreateAPIView,
    ProfessionalReviewRetrieveUpdateDeleteAPIView,
    CombinedCredentialRecordAPIView,
    ProfessionalCredentialListAPIView,
    Stage2SubmitAPIView,
    ProfessionalReviewDecisionAPIView,
    ProfessionalReviewResubmitAPIView,
    ProfessionalReviewStatusAPIView,
)

app_name = "professionals"

urlpatterns = [
    path("professional-profiles/", ProfessionalProfileListCreateAPIView.as_view(), name="professional-profile-list-create"),
    path("professional-profiles/<int:pk>/", ProfessionalProfileRetrieveUpdateDeleteAPIView.as_view(), name="professional-profile-detail"),
    path("professional-profiles/<int:prof_id>/stage2_submit/", Stage2SubmitAPIView.as_view(), name="professional-profile-stage2-submit"),
    path("professional-profiles/<int:prof_id>/stage2_resubmit/", ProfessionalReviewResubmitAPIView.as_view(), name="professional-profile-stage2-resubmit"),
    path("professional-profiles/<int:prof_id>/stage2_status/", ProfessionalReviewStatusAPIView.as_view(), name="professional-profile-stage2-status"),
    path("professional-reviews/", ProfessionalReviewListCreateAPIView.as_view(), name="professional-review-list-create"),
    path("professional-reviews/<int:pk>/", ProfessionalReviewRetrieveUpdateDeleteAPIView.as_view(), name="professional-review-detail"),
    path("professional-reviews/<int:review_id>/decision/", ProfessionalReviewDecisionAPIView.as_view(), name="professional-review-decision"),
    path("credential-records/", CredentialRecordListCreateAPIView.as_view(), name="credential-record-list-create"),
    path("credential-records/<int:pk>/", CredentialRecordRetrieveUpdateDeleteAPIView.as_view(), name="credential-record-detail"),
    path("capability-records/", CapabilityRecordListCreateAPIView.as_view(), name="capability-record-list-create"),
    path("capability-records/<int:pk>/", CapabilityRecordRetrieveUpdateDeleteAPIView.as_view(), name="capability-record-detail"),
    path("contact-records/", ContactRecordListCreateAPIView.as_view(), name="contact-record-list-create"),
    path("contact-records/<int:pk>/", ContactRecordRetrieveUpdateDeleteAPIView.as_view(), name="contact-record-detail"),

    path("combined-credential-record/",CombinedCredentialRecordAPIView.as_view(),name="combined-credential-record-create"),
    path("combined-credential-record/<int:pk>/",CombinedCredentialRecordAPIView.as_view(),name="combined-credential-record-update"), 
    
    path("professional/<int:professional_id>/credentials/", ProfessionalCredentialListAPIView.as_view(), name="professional-credentials"), 
]
