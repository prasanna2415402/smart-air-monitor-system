from django.contrib import admin

from apps.backup.models import BackupRecord, RestoreRecord


@admin.register(BackupRecord)
class BackupRecordAdmin(admin.ModelAdmin):
    list_display = ["file_name", "backup_type", "status", "file_size_bytes", "created_at"]
    list_filter = ["backup_type", "status"]


@admin.register(RestoreRecord)
class RestoreRecordAdmin(admin.ModelAdmin):
    list_display = ["source_file_name", "status", "created_at"]
    list_filter = ["status"]
