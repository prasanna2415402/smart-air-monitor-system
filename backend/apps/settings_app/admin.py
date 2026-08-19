from django.contrib import admin

from apps.settings_app.models import SystemSettings


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ["theme", "auto_refresh_enabled", "aqi_warning", "aqi_critical", "updated_at"]

    def has_add_permission(self, request):
        return not SystemSettings.objects.exists()
