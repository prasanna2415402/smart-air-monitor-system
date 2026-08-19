from django.contrib import admin

from apps.stations.models import Station


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "status", "location", "sensor_count", "created_at"]
    list_filter = ["status"]
    search_fields = ["name", "code", "location"]
