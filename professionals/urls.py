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
)

app_name = "professionals"

urlpatterns = [
    path("professional-profiles/", ProfessionalProfileListCreateAPIView.as_view(), name="professional-profile-list-create"),
    path("professional-profiles/<int:pk>/", ProfessionalProfileRetrieveUpdateDeleteAPIView.as_view(), name="professional-profile-detail"),
    path("professional-reviews/", ProfessionalReviewListCreateAPIView.as_view(), name="professional-review-list-create"),
    path("professional-reviews/<int:pk>/", ProfessionalReviewRetrieveUpdateDeleteAPIView.as_view(), name="professional-review-detail"),
    path("credential-records/", CredentialRecordListCreateAPIView.as_view(), name="credential-record-list-create"),
    path("credential-records/<int:pk>/", CredentialRecordRetrieveUpdateDeleteAPIView.as_view(), name="credential-record-detail"),
    path("capability-records/", CapabilityRecordListCreateAPIView.as_view(), name="capability-record-list-create"),
    path("capability-records/<int:pk>/", CapabilityRecordRetrieveUpdateDeleteAPIView.as_view(), name="capability-record-detail"),
    path("contact-records/", ContactRecordListCreateAPIView.as_view(), name="contact-record-list-create"),
    path("contact-records/<int:pk>/", ContactRecordRetrieveUpdateDeleteAPIView.as_view(), name="contact-record-detail"),
]
