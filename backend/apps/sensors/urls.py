from rest_framework.routers import DefaultRouter

from apps.sensors.views import AlertLogViewSet, SensorReadingIngestView, SensorReadingViewSet, SensorViewSet
from django.urls import path, include

router = DefaultRouter()
router.register("readings", SensorReadingViewSet, basename="sensor-reading")
router.register("alerts", AlertLogViewSet, basename="alert-log")
router.register("", SensorViewSet, basename="sensor")

urlpatterns = [
    path("ingest/", SensorReadingIngestView.as_view(), name="sensor-ingest"),
    path("", include(router.urls)),
]
