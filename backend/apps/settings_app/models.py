from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TimeStampedModel


class SystemSettings(TimeStampedModel):
    """
    Singleton settings record — mirrors the original Streamlit prototype's
    Settings page: COM port & baud rate, theme, auto-refresh, and every
    alarm threshold (CO2, temperature, humidity, PM2.5, PM10, AQI).

    Enforced as a singleton (id is always 1) since the whole facility shares
    one active configuration; use `SystemSettings.get_solo()` to fetch it.
    """

    class Theme(models.TextChoices):
        LIGHT = "LIGHT", "Light"
        DARK = "DARK", "Dark"

    # --- Data source / hardware ---
    com_port = models.CharField(max_length=50, blank=True, default="")
    baud_rate = models.IntegerField(default=115200)

    # --- UI preferences ---
    theme = models.CharField(max_length=10, choices=Theme.choices, default=Theme.DARK)
    auto_refresh_enabled = models.BooleanField(default=True)
    auto_refresh_interval_seconds = models.PositiveIntegerField(default=5)

    # --- Alarm thresholds (mirrors alerts.DEFAULT_THRESHOLDS) ---
    co2_warning = models.FloatField(default=1000)
    co2_critical = models.FloatField(default=1500)
    co_warning = models.FloatField(default=9)
    co_critical = models.FloatField(default=35)
    voc_warning = models.FloatField(default=150)
    voc_critical = models.FloatField(default=300)
    temp_warning = models.FloatField(default=28)
    temp_critical = models.FloatField(default=35)
    humidity_high_warning = models.FloatField(default=70)
    humidity_high_critical = models.FloatField(default=85)
    humidity_low_warning = models.FloatField(default=30)
    humidity_low_critical = models.FloatField(default=20)
    pm25_warning = models.FloatField(default=25)
    pm25_critical = models.FloatField(default=75)
    pm10_warning = models.FloatField(default=50)
    pm10_critical = models.FloatField(default=150)
    aqi_warning = models.FloatField(default=100)
    aqi_critical = models.FloatField(default=150)

    updated_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )

    class Meta:
        db_table = "system_settings"
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("The singleton SystemSettings record cannot be deleted.")

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def as_thresholds_dict(self):
        return {
            "co2_warning": self.co2_warning, "co2_critical": self.co2_critical,
            "co_warning": self.co_warning, "co_critical": self.co_critical,
            "voc_warning": self.voc_warning, "voc_critical": self.voc_critical,
            "temp_warning": self.temp_warning, "temp_critical": self.temp_critical,
            "hum_high_warning": self.humidity_high_warning, "hum_high_critical": self.humidity_high_critical,
            "hum_low_warning": self.humidity_low_warning, "hum_low_critical": self.humidity_low_critical,
            "pm25_warning": self.pm25_warning, "pm25_critical": self.pm25_critical,
            "pm10_warning": self.pm10_warning, "pm10_critical": self.pm10_critical,
            "aqi_warning": self.aqi_warning, "aqi_critical": self.aqi_critical,
        }

    def __str__(self):
        return "System Settings"
