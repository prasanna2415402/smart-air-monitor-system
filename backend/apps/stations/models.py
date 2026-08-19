from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Station(TimeStampedModel):
    """
    A monitoring station / zone (e.g. 'Zone A - Production', 'Zone B -
    Warehouse') as shown on the dashboard's 'Live Sensor Readings' panel.
    """

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        MAINTENANCE = "MAINTENANCE", "Maintenance"

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30, unique=True, help_text="Short unique code, e.g. ZONE-A")
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="stations_created",
    )

    class Meta:
        db_table = "stations"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def sensor_count(self):
        return self.sensors.count()

    @property
    def online_sensor_count(self):
        return self.sensors.filter(status="ONLINE").count()
