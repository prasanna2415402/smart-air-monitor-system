from django.urls import path

from apps.settings_app.views import SystemSettingsResetView, SystemSettingsView

urlpatterns = [
    path("", SystemSettingsView.as_view(), name="system-settings"),
    path("reset/", SystemSettingsResetView.as_view(), name="system-settings-reset"),
]
