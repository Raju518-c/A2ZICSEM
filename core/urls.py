from django.urls import path

from .views import (
    GlobalDynamicTableFilterAPIView,
    ProfessionalProfileRelatedRecordsAPIView,
)

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
]
