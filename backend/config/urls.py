"""
URL configuration for the BioLab project.
All API routes are prefixed with /api/.
Swagger UI available at /api/docs/ (DEBUG only).
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # API Endpoints
    path("api/auth/", include("accounts.urls")),
    path("api/substances/", include("substances.urls")),
    path("api/hazards/", include("hazards.urls")),
    path("api/compatibility/", include("compatibility.urls")),
    path("api/", include("fispq.urls")),
]

# API Documentation — only in DEBUG
if settings.DEBUG:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularSwaggerView,
        SpectacularRedocView,
    )
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
