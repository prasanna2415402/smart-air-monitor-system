from django.contrib import admin

from apps.sensors.models import AlertLog, Sensor, SensorReading


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ["name", "station", "sensor_type", "status", "serial_number"]
    list_filter = ["sensor_type", "status", "station"]
    search_fields = ["name", "serial_number"]


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ["station", "timestamp", "co2_ppm", "pm25", "pm10", "aqi_score", "alert_level"]
    list_filter = ["alert_level", "station"]
    date_hierarchy = "timestamp"


@admin.register(AlertLog)
class AlertLogAdmin(admin.ModelAdmin):
    list_display = ["station", "parameter", "severity", "is_acknowledged", "created_at"]
    list_filter = ["severity", "is_acknowledged", "station"]
