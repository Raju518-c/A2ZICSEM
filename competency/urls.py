from django.urls import path
from .views import *
app_name = "competency"






urlpatterns = [

    path(
        "professional-scopes/",
        ProfessionalScopeListCreateAPIView.as_view(),
        name="professional-scope-list-create",
    ),

    path(
        "professional-scopes/<int:pk>/",
        ProfessionalScopeRetrieveUpdateDeleteAPIView.as_view(),
        name="professional-scope-detail",
    ),





    path(
        "competency-assessments/",
        CompetencyAssessmentListCreateAPIView.as_view(),
        name="competency-assessment-list-create",
    ),

    path(
        "competency-assessments/<int:pk>/",
        CompetencyAssessmentRetrieveUpdateDeleteAPIView.as_view(),
        name="competency-assessment-detail",
    ),
]






