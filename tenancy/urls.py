from django.urls import path

from .views import (
    TenantListCreateAPIView,
    TenantOperationListCreateAPIView,
    TenantOperationRetrieveUpdateDeleteAPIView,
    TenantRetrieveUpdateDeleteAPIView,
    OrganizationListCreateAPIView,
    OrganizationRetrieveUpdateDeleteAPIView,
    TenantCombinedCreateAPIView,
)

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
        "organizations/",
        OrganizationListCreateAPIView.as_view(),
        name="organization-list-create",
    ),

    path(
        "organizations/<uuid:pk>/",
        OrganizationRetrieveUpdateDeleteAPIView.as_view(),
        name="organization-detail",
    ),    
]
