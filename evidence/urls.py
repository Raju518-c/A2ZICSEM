from django.urls import path
from .views import *

app_name = "evidence"

urlpatterns = [
    path(
        "evidence-documents/",
        EvidenceDocumentListCreateAPIView.as_view(),
        name="evidence-document-list-create",
    ),

    path(
        "evidence-documents/<uuid:pk>/",
        EvidenceDocumentRetrieveUpdateDeleteAPIView.as_view(),
        name="evidence-document-detail",
    ),
]
