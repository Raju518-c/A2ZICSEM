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
    
    path("tenant-invitations/", TenantRegistrationInviteListCreateAPIView.as_view(), name="tenant-invitation-list-create"),
    path("tenant-invitations/<int:pk>/", TenantRegistrationInviteDetailAPIView.as_view(), name="tenant-invitation-detail"),            
    path("tenant-registration-invite/<uuid:token>/", TenantRegistrationInviteByTokenAPIView.as_view(), name="tenant-registration-invite-by-token",),
]
