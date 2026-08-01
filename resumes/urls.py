from django.urls import path
from .views import *
app_name = "resumes"

urlpatterns = [


    path(
        "resume-templates/",
        ResumeTemplateListCreateAPIView.as_view(),
        name="resume-template-list-create",
    ),

    path(
        "resume-templates/<int:pk>/",
        ResumeTemplateRetrieveUpdateDeleteAPIView.as_view(),
        name="resume-template-detail",
    ),

    path(
        "resume-generations/",
        ResumeGenerationListCreateAPIView.as_view(),
        name="resume-generation-list-create",
    ),

    path(
        "resume-generations/<uuid:pk>/",
        ResumeGenerationRetrieveUpdateDeleteAPIView.as_view(),
        name="resume-generation-detail",
    ),
]
