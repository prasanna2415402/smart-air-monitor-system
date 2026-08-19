from rest_framework import serializers

from apps.sensors.models import AlertLog, Sensor, SensorReading
from apps.stations.models import Station


class SensorSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source="station.name", read_only=True)

    class Meta:
        model = Sensor
        fields = [
            "id", "station", "station_name", "name", "sensor_type", "serial_number",
            "unit", "status", "last_calibrated", "installed_at", "firmware_version",
            "created_by", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]


class SensorReadingSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source="station.name", read_only=True)

    class Meta:
        model = SensorReading
        fields = [
            "id", "station", "station_name", "sensor", "timestamp",
            "co2_ppm", "co_ppm", "voc_index", "temperature", "humidity","mq135_raw", "pm25", "pm10", "pressure",
            "aqi_score", "alert_level", "fan_state",
        ]
        read_only_fields = ["id", "timestamp", "aqi_score", "alert_level"]


class SensorReadingIngestSerializer(serializers.Serializer):
    """
    Input shape for the ingest endpoint.
    DHT22 currently provides temperature and humidity.
    MQ135 provides raw ADC value.
    Other sensor values are optional for now.
    """

    station = serializers.PrimaryKeyRelatedField(
        queryset=Station.objects.all()
    )

    sensor = serializers.PrimaryKeyRelatedField(
        queryset=Sensor.objects.all(),
        required=False,
        allow_null=True
    )

    co2_ppm = serializers.FloatField(
        min_value=0,
        required=False,
        default=0.0
    )

    co_ppm = serializers.FloatField(
        min_value=0,
        required=False,
        default=0.0
    )

    voc_index = serializers.FloatField(
        min_value=0,
        required=False,
        default=0.0
    )

    temperature = serializers.FloatField()

    humidity = serializers.FloatField(
        min_value=0,
        max_value=100
    )

    mq135_raw = serializers.IntegerField(
        min_value=0,
        max_value=4095,
        required=False,
        default=0
    )

    pm25 = serializers.FloatField(
        min_value=0,
        required=False,
        default=0.0
    )

    pm10 = serializers.FloatField(
        min_value=0,
        required=False,
        default=0.0
    )

    pressure = serializers.FloatField(
        min_value=0,
        required=False,
        default=0.0
    )

    fan_state = serializers.BooleanField(
        required=False,
        default=False
    )

class AlertLogSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source="station.name", read_only=True)
    acknowledged_by_name = serializers.CharField(source="acknowledged_by.full_name", read_only=True, default=None)

    class Meta:
        model = AlertLog
        fields = [
            "id", "station", "station_name", "reading", "parameter", "severity",
            "message", "recommendation", "is_acknowledged", "acknowledged_by",
            "acknowledged_by_name", "acknowledged_at", "created_at",
        ]
        read_only_fields = [
            "id", "station", "reading", "parameter", "severity", "message",
            "recommendation", "acknowledged_by", "acknowledged_at", "created_at",
        ]


class DailyReportSerializer(serializers.Serializer):
    bucket = serializers.CharField()
    avg_co2 = serializers.FloatField()
    avg_co = serializers.FloatField()
    avg_voc = serializers.FloatField()
    avg_temp = serializers.FloatField()
    avg_hum = serializers.FloatField()
    avg_pm25 = serializers.FloatField()
    avg_pm10 = serializers.FloatField()
    avg_pressure = serializers.FloatField()
    avg_aqi = serializers.FloatField(allow_null=True)
    n_readings = serializers.IntegerField()
