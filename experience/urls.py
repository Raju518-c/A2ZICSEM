from django.urls import path
from .views import *
app_name = "experience"

urlpatterns = [


    path(
        "employment-records/",
        EmploymentRecordListCreateAPIView.as_view(),
        name="employment-record-list-create",
    ),

    path(
        "employment-records/<int:pk>/",
        EmploymentRecordRetrieveUpdateDeleteAPIView.as_view(),
        name="employment-record-detail",
    ),

    path(
        "project-records/",
        ProjectRecordListCreateAPIView.as_view(),
        name="project-record-list-create",
    ),

    path(
        "project-records/bulk/",
        BulkProjectRecordCreateAPIView.as_view(),
        name="bulk-project-record-create",
    ),

    path(
        "project-records/<uuid:pk>/",
        ProjectRecordRetrieveUpdateDeleteAPIView.as_view(),
        name="project-record-detail",
    ),

    path(
        "project-scopes/",
        ProjectScopeListCreateAPIView.as_view(),
        name="project-scope-list-create",
    ),

    path(
        "project-scopes/<int:pk>/dynamic-form/",
        ProjectScopeDynamicFormAPIView.as_view(),
        name="project-scope-dynamic-form",
    ),

    path(
        "project-scopes/<int:pk>/",
        ProjectScopeRetrieveUpdateDeleteAPIView.as_view(),
        name="project-scope-detail",
    ),

    path(
        "scope-responses/",
        ScopeResponseListCreateAPIView.as_view(),
        name="scope-response-list-create",
    ),

    path(
        "scope-responses/<int:pk>/",
        ScopeResponseRetrieveUpdateDeleteAPIView.as_view(),
        name="scope-response-detail",
    ),

    path(
        "exposure-logs/",
        ExposureLogListCreateAPIView.as_view(),
        name="exposure-log-list-create",
    ),

    path(
        "exposure-logs/<int:pk>/",
        ExposureLogRetrieveUpdateDeleteAPIView.as_view(),
        name="exposure-log-detail",
    ),

    path(
        "professional-assignments/",
        ProfessionalAssignmentListCreateAPIView.as_view(),
        name="professional-assignment-list-create",
    ),

    path(
        "professional-assignments/<int:pk>/",
        ProfessionalAssignmentRetrieveUpdateDeleteAPIView.as_view(),
        name="professional-assignment-detail",
    ),
    
    path("Validate-Experience", ValidateExperienceTabAPIView.as_view()),
]
