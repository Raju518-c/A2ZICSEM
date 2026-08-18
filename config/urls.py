from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "api/schema/",
        staff_member_required(
            SpectacularAPIView.as_view()
        ),
        name="schema",
    ),

    path(
        "swagger/",
        staff_member_required(
            SpectacularSwaggerView.as_view(url_name="schema")
        ),
        name="swagger-ui",
    ),

    path(
        "api/redoc/",
        staff_member_required(
            SpectacularRedocView.as_view(url_name="schema")
        ),
        name="redoc",
    ),
    
    path("",include("core.urls")),
    path("", include("tenancy.urls")),
    path("", include("accounts.urls")),
    path("",include("professionals.urls")),
    path("", include("catalog.urls")),
    path("",include("experience.urls")),
    path("",include("evidence.urls")),
    path("",include("competency.urls")),
    path("",include("resumes.urls")),   
    path("",include("governance.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
