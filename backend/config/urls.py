from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Smart Air Monitor System API",
        default_version="v1",
        description=(
            "REST API for the Smart Air Monitor System — Users, Stations, "
            "Sensors & Readings, Dashboard, Settings, AI/ML Predictions, "
            "and Database Backup/Restore."
        ),
        contact=openapi.Contact(email="admin@smartair.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # --- API v1 ---
    path("api/", include("apps.accounts.urls")),
    path("api/stations/", include("apps.stations.urls")),
    path("api/sensors/", include("apps.sensors.urls")),
    path("api/dashboard/", include("apps.dashboard.urls")),
    path("api/settings/", include("apps.settings_app.urls")),
    path("api/backup/", include("apps.backup.urls")),
    path("api/ai/", include("apps.ai.urls")),

    # --- API documentation ---
    path("api/docs/swagger.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("api/docs/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
