from django.conf import settings
from django.db import models


class BackupRecord(models.Model):
    """
    Audit log of every database backup/restore operation, plus a reference
    to the generated dump file so Admins can list, download, or clean up
    old backups from the 'Database Backup/Restore' settings page.
    """

    class BackupType(models.TextChoices):
        FULL = "FULL", "Full Database (JSON fixture)"
        SENSORS_ONLY = "SENSORS_ONLY", "Sensor Readings Only"

    class Status(models.TextChoices):
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"

    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size_bytes = models.BigIntegerField(default=0)
    backup_type = models.CharField(max_length=20, choices=BackupType.choices, default=BackupType.FULL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    error_message = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="backups_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "backup_records"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.file_name} ({self.status})"


class RestoreRecord(models.Model):
    """Audit log of every restore-from-backup operation."""

    class Status(models.TextChoices):
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    source_file_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices)
    error_message = models.TextField(blank=True, null=True)
    restored_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="restores_performed",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "restore_records"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Restore of {self.source_file_name} ({self.status})"
