# training/combined_urls.py

from django.urls import path
from .views import *

urlpatterns = [
    # TrainingProgram + TrainingModule
    path("program-with-modules/", TrainingProgramWithModulesListCreateAPIView.as_view(), name="program-with-modules-list-create"),
    path("program-with-modules/<int:pk>/", TrainingProgramWithModulesDetailAPIView.as_view(), name="program-with-modules-detail"),

    # QuestionBank + QuestionOption
    path("questions-with-options/", QuestionBankWithOptionsListCreateAPIView.as_view(), name="questions-with-options-list-create"),
    path("questions-with-options/<int:pk>/", QuestionBankWithOptionsDetailAPIView.as_view(), name="questions-with-options-detail"),

    # TrainingAssessment + AssessmentQuestionConfig
    path("assessment-with-configs/", TrainingAssessmentWithConfigsListCreateAPIView.as_view(), name="assessment-with-configs-list-create"),
    path("assessment-with-configs/<int:pk>/", TrainingAssessmentWithConfigsDetailAPIView.as_view(), name="assessment-with-configs-detail"),

    # Tenant imports
    path("tenant-programs/import/", TenantTrainingProgramImportAPIView.as_view(), name="tenant-program-import"),
    path("tenant-programs/import/<int:pk>/", TenantTrainingProgramImportDetailAPIView.as_view(), name="tenant-program-import-detail"),
    path("tenant-assessments/import/", TenantAssessmentImportAPIView.as_view(), name="tenant-assessment-import"),
    path("tenant-assessments/import/<int:pk>/", TenantAssessmentImportDetailAPIView.as_view(), name="tenant-assessment-import-detail"),
    
    path('content-assignments/',ContentAssignmentListCreate.as_view()),
    path('content-assignments/my-access/',MyContentAccess.as_view()),
    path('content-assignments/<int:pk>/revoke/',RevokeContentAssignment.as_view()),
]
