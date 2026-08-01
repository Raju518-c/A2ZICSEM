from django.urls import path

from .views import (
    FormFieldListCreateAPIView,
    FormFieldRetrieveUpdateDeleteAPIView,
    FormModuleListCreateAPIView,
    FormModuleRetrieveUpdateDeleteAPIView,
    ReferenceValueListCreateAPIView,
    ReferenceValueRetrieveUpdateDeleteAPIView,
    ScopeCatalogListCreateAPIView,
    ScopeCatalogRetrieveUpdateDeleteAPIView,
    ScopeModuleListCreateAPIView,
    ScopeModuleRetrieveUpdateDeleteAPIView,
)

app_name = "catalog"

urlpatterns = [
    path(
        "reference-values/",
        ReferenceValueListCreateAPIView.as_view(),
        name="reference-value-list-create",
    ),
    path(
        "reference-values/<int:pk>/",
        ReferenceValueRetrieveUpdateDeleteAPIView.as_view(),
        name="reference-value-detail",
    ),
    path(
        "scope-catalogs/",
        ScopeCatalogListCreateAPIView.as_view(),
        name="scope-catalog-list-create",
    ),
    path(
        "scope-catalogs/<int:pk>/",
        ScopeCatalogRetrieveUpdateDeleteAPIView.as_view(),
        name="scope-catalog-detail",
    ),
    path(
        "form-modules/",
        FormModuleListCreateAPIView.as_view(),
        name="form-module-list-create",
    ),
    path(
        "form-modules/<int:pk>/",
        FormModuleRetrieveUpdateDeleteAPIView.as_view(),
        name="form-module-detail",
    ),
    path(
        "scope-modules/",
        ScopeModuleListCreateAPIView.as_view(),
        name="scope-module-list-create",
    ),
    path(
        "scope-modules/<int:pk>/",
        ScopeModuleRetrieveUpdateDeleteAPIView.as_view(),
        name="scope-module-detail",
    ),
    path(
        "form-fields/",
        FormFieldListCreateAPIView.as_view(),
        name="form-field-list-create",
    ),
    path(
        "form-fields/<int:pk>/",
        FormFieldRetrieveUpdateDeleteAPIView.as_view(),
        name="form-field-detail",
    ),
]
