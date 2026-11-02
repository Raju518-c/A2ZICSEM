from django.urls import path

from .views import *

urlpatterns = [
    path(
        "ecosystem-members/",
        EcosystemMemberListCreateAPIView.as_view(),
        name="ecosystem-member-list-create"
    ),

    path(
        "ecosystem-members/<int:pk>/",
        EcosystemMemberDetailAPIView.as_view(),
        name="ecosystem-member-detail"
    ),
]