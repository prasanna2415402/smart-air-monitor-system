from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel
from apps.stations.models import Station


class Sensor(TimeStampedModel):
    """An individual physical sensor/probe installed at a Station."""

    class SensorType(models.TextChoices):
        CO2 = "CO2", "CO2"
        CO = "CO", "Carbon Monoxide"
        VOC = "VOC", "VOC"
        TEMPERATURE = "TEMPERATURE", "Temperature"
        HUMIDITY = "HUMIDITY", "Humidity"
        PM25 = "PM25", "PM2.5"
        PM10 = "PM10", "PM10"
        PRESSURE = "PRESSURE", "Pressure"
        MULTI = "MULTI", "Multi-parameter (all-in-one)"

    class Status(models.TextChoices):
        ONLINE = "ONLINE", "Online"
        OFFLINE = "OFFLINE", "Offline"
        MAINTENANCE = "MAINTENANCE", "Maintenance"
        FAULT = "FAULT", "Fault"

    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="sensors")
    name = models.CharField(max_length=150)
    sensor_type = models.CharField(max_length=20, choices=SensorType.choices, default=SensorType.MULTI)
    serial_number = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ONLINE)

    last_calibrated = models.DateField(null=True, blank=True)
    installed_at = models.DateField(null=True, blank=True)
    firmware_version = models.CharField(max_length=30, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="sensors_created",
    )

    class Meta:
        db_table = "sensors"
        ordering = ["station__name", "name"]

    def __str__(self):
        return f"{self.name} @ {self.station.code}"


class SensorReading(models.Model):
    """
    A composite air-quality reading for a Station, matching the schema of
    the original Streamlit prototype's `air_quality_readings` table
    (co2_ppm, temperature, humidity, pm25, pm10, pressure, aqi_score,
    alert_level, fan_state) — now attributed to a Station/Sensor and
    exposed over the REST API instead of raw SQLite.
    """

    class AlertLevel(models.TextChoices):
        GOOD = "GOOD", "Good"
        MODERATE = "MODERATE", "Moderate"
        POOR = "POOR", "Poor"
        VERY_POOR = "VERY_POOR", "Very Poor"
        HAZARDOUS = "HAZARDOUS", "Hazardous"

    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="readings")
    sensor = models.ForeignKey(
        Sensor, on_delete=models.SET_NULL, null=True, blank=True, related_name="readings"
    )
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    co2_ppm = models.FloatField()
    co_ppm = models.FloatField(default=0.0, help_text="Carbon monoxide, parts per million.")
    voc_index = models.FloatField(default=0.0, help_text="Volatile organic compound index (0-500 scale).")
    temperature = models.FloatField()
    humidity = models.FloatField()
    pm25 = models.FloatField()
    pm10 = models.FloatField()
    pressure = models.FloatField()
    mq135_raw = models.IntegerField(
    default=0,
    help_text="Raw ADC value from MQ135 sensor (0-4095)."
)

    aqi_score = models.FloatField(null=True, blank=True)
    alert_level = models.CharField(max_length=20, choices=AlertLevel.choices, null=True, blank=True)
    fan_state = models.BooleanField(default=False)

    class Meta:
        db_table = "sensor_readings"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["station", "timestamp"]),
            models.Index(fields=["alert_level"]),
        ]

    def __str__(self):
        return f"{self.station.code} @ {self.timestamp:%Y-%m-%d %H:%M} (AQI {self.aqi_score})"


class AlertLog(TimeStampedModel):
    """Threshold-breach alert log entry, tied to the reading that triggered it."""

    class Severity(models.TextChoices):
        WARNING = "WARNING", "Warning"
        CRITICAL = "CRITICAL", "Critical"

    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="alerts")
    reading = models.ForeignKey(
        SensorReading, on_delete=models.CASCADE, related_name="alerts", null=True, blank=True
    )
    parameter = models.CharField(max_length=30, help_text="e.g. CO2, PM2.5, HUMIDITY")
    severity = models.CharField(max_length=20, choices=Severity.choices)
    message = models.CharField(max_length=255)
    recommendation = models.CharField(max_length=255, blank=True)

    is_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="acknowledged_alerts",
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "alert_logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.severity}] {self.station.code}: {self.message}"
