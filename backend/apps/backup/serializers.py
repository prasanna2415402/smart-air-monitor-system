from rest_framework import serializers

from apps.backup.models import BackupRecord, RestoreRecord


class BackupRecordSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)
    file_size_kb = serializers.SerializerMethodField()

    class Meta:
        model = BackupRecord
        fields = [
            "id", "file_name", "file_size_bytes", "file_size_kb", "backup_type",
            "status", "error_message", "created_by", "created_by_name", "created_at",
        ]
        read_only_fields = fields

    def get_file_size_kb(self, obj):
        return round(obj.file_size_bytes / 1024, 2)


class RestoreRecordSerializer(serializers.ModelSerializer):
    restored_by_name = serializers.CharField(source="restored_by.full_name", read_only=True, default=None)

    class Meta:
        model = RestoreRecord
        fields = ["id", "source_file_name", "status", "error_message", "restored_by", "restored_by_name", "created_at"]
        read_only_fields = fields


class RestoreUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    confirm = serializers.BooleanField(
        help_text="Must be true — restoring overwrites existing data for the restored models."
    )

    def validate_confirm(self, value):
        if not value:
            raise serializers.ValidationError(
                "You must set confirm=true to acknowledge this will overwrite existing data."
            )
        return value

    def validate_file(self, value):
        if not value.name.endswith(".json"):
            raise serializers.ValidationError("Only .json fixture files produced by the backup endpoint are supported.")
        return value
