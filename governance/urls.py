from django.urls import path
from .views import *

app_name = "governance"

urlpatterns = [
    path(
        "audit-events/",
        AuditEventListCreateAPIView.as_view(),
        name="audit-event-list-create",
    ),

    path(
        "audit-events/<int:pk>/",
        AuditEventRetrieveUpdateDeleteAPIView.as_view(),
        name="audit-event-detail",
    ),
]
