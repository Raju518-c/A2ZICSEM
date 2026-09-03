from django.urls import path

from .views import *

app_name = "core"

urlpatterns = [
    path(
        "professional-profiles/<int:pk>/related-records/",
        ProfessionalProfileRelatedRecordsAPIView.as_view(),
        name="professional-profile-related-records",
    ),
    path(
        "global-dynamic-filter/",
        GlobalDynamicTableFilterAPIView.as_view(),
        name="global-dynamic-filter",
    ),
    
    path("tenant-reg-invitations/", TenantRegistrationInviteListCreateAPIView.as_view(), name="tenant-reg-invitation-list-create"),
    path("tenant-reg-invitations/<int:pk>/", TenantRegistrationInviteDetailAPIView.as_view(), name="tenant-reg-invitation-detail"),            
    path("tenant-registration-invite-check/<uuid:token>/", TenantRegistrationInviteByTokenAPIView.as_view(), name="tenant-registration-invite-check-token",),
]
