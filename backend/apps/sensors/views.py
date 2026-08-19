from datetime import timedelta

from django.db.models import Avg, Count, Max
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin, IsOperatorOrAdmin, IsViewerOrAbove
from apps.core.responses import error_response, success_response
from apps.sensors import alerts as alert_engine
from apps.sensors.models import AlertLog, Sensor, SensorReading
from apps.sensors.serializers import (
    AlertLogSerializer,
    DailyReportSerializer,
    SensorReadingIngestSerializer,
    SensorReadingSerializer,
    SensorSerializer,
)
from apps.settings_app.models import SystemSettings


class SensorViewSet(viewsets.ModelViewSet):
    """Full CRUD for individual sensors/probes."""

    queryset = Sensor.objects.select_related("station").all()
    serializer_class = SensorSerializer
    permission_classes = [IsViewerOrAbove, IsOperatorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["station", "sensor_type", "status"]
    search_fields = ["name", "serial_number"]
    ordering_fields = ["created_at", "name"]
    ordering = ["station__name", "name"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(data=serializer.data, message="Sensor created successfully.", status=201)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Sensor updated successfully.")

    def destroy(self, request, *args, **kwargs):
        self.perform_destroy(self.get_object())
        return success_response(message="Sensor deleted successfully.")


class SensorReadingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only browsing of historical readings, matching the original
    prototype's History page: date-range, alert-level, and AQI-range
    filters/search.
    """

    queryset = SensorReading.objects.select_related("station", "sensor").all()
    serializer_class = SensorReadingSerializer
    permission_classes = [IsViewerOrAbove]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["station", "sensor", "alert_level"]
    ordering_fields = ["timestamp", "aqi_score"]
    ordering = ["-timestamp"]

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        start = params.get("start")
        end = params.get("end")
        min_aqi = params.get("min_aqi")
        max_aqi = params.get("max_aqi")
        minutes = params.get("recent_minutes")

        if start:
            dt = parse_datetime(start)
            if dt:
                qs = qs.filter(timestamp__gte=dt)
        if end:
            dt = parse_datetime(end)
            if dt:
                qs = qs.filter(timestamp__lte=dt)
        if minutes:
            since = timezone.now() - timedelta(minutes=int(minutes))
            qs = qs.filter(timestamp__gte=since)
        if min_aqi:
            qs = qs.filter(aqi_score__gte=float(min_aqi))
        if max_aqi:
            qs = qs.filter(aqi_score__lte=float(max_aqi))
        return qs

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.AllowAny],
    )
    def latest(self, request):
        """GET /api/sensors/readings/latest/?station=4&n=1"""

        station_id = request.query_params.get("station")
        n = int(request.query_params.get("n", 1))

        qs = self.get_queryset()

        if station_id:
            qs = qs.filter(station_id=station_id)

        data = SensorReadingSerializer(
            qs.order_by("-timestamp")[:n],
            many=True
        ).data

        return success_response(data=data)
class SensorReadingIngestView(APIView):
    """
    POST /api/sensors/ingest/ — used by the ESP32 firmware / simulator (or
    any external data source) to push a new composite reading. Computes
    aqi_score, alert_level, and fan_state exactly like the original
    prototype's data_source.py + alerts.py, and raises AlertLog rows for
    any breached threshold.
    """

    permission_classes = [permissions.AllowAny]
    throttle_scope = "ingest"

    def post(self, request):
        serializer = SensorReadingIngestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        settings_obj = SystemSettings.get_solo()
        thresholds = settings_obj.as_thresholds_dict()

        aqi = alert_engine.calculate_aqi(payload)
        alert_level = alert_engine.classify_alert_level(aqi)
        fan_state = alert_engine.fan_hysteresis(payload.get("fan_state", False), aqi, thresholds)

        reading = SensorReading.objects.create(
            station=payload["station"],
            sensor=payload.get("sensor"),
            co2_ppm=payload["co2_ppm"],
            co_ppm=payload.get("co_ppm", 0.0),
            voc_index=payload.get("voc_index", 0.0),
            temperature=payload["temperature"],
            humidity=payload["humidity"],
            mq135_raw=payload.get("mq135_raw", 0),
            pm25=payload["pm25"],
            pm10=payload["pm10"],
            pressure=payload["pressure"],
            aqi_score=aqi,
            alert_level=alert_level,
            fan_state=fan_state,
        )

        breaches = alert_engine.check_thresholds(payload, thresholds)
        alert_objs = [
            AlertLog(
                station=payload["station"], reading=reading, parameter=b["parameter"],
                severity=b["severity"], message=b["message"], recommendation=b["recommendation"],
            )
            for b in breaches
        ]
        AlertLog.objects.bulk_create(alert_objs)

        return success_response(
            data={
                "reading": SensorReadingSerializer(reading).data,
                "alerts_raised": len(alert_objs),
            },
            message="Reading ingested successfully.",
            status=status.HTTP_201_CREATED,
        )


class AlertLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only alert log browsing + acknowledge action."""

    queryset = AlertLog.objects.select_related("station", "acknowledged_by").all()
    serializer_class = AlertLogSerializer
    permission_classes = [IsViewerOrAbove]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["station", "severity", "is_acknowledged"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"], permission_classes=[IsOperatorOrAdmin])
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        alert.is_acknowledged = True
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        return success_response(data=AlertLogSerializer(alert).data, message="Alert acknowledged.")
