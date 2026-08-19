import io
import logging
from datetime import datetime

from django.conf import settings
from django.core.management import call_command
from django.http import FileResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView

from apps.backup.models import BackupRecord, RestoreRecord
from apps.backup.serializers import (
    BackupRecordSerializer,
    RestoreRecordSerializer,
    RestoreUploadSerializer,
)
from apps.core.permissions import IsAdmin
from apps.core.responses import error_response, success_response

logger = logging.getLogger("apps")

# Only these apps' data are included in a backup — auth/session/contenttype
# framework tables are deliberately excluded since they're environment-specific.
BACKUP_APP_LABELS = [
    "accounts", "stations", "sensors", "settings_app",
]


class BackupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET    /api/backup/                — list all backups
    GET    /api/backup/{id}/           — backup details
    POST   /api/backup/create_backup/  — create a new full backup (JSON fixture)
    GET    /api/backup/{id}/download/  — download a backup file
    DELETE /api/backup/{id}/           — delete a backup record + file
    """

    queryset = BackupRecord.objects.select_related("created_by").all()
    serializer_class = BackupRecordSerializer
    permission_classes = [IsAdmin]

    @action(detail=False, methods=["post"])
    def create_backup(self, request):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"backup_{timestamp}.json"
        file_path = settings.BACKUP_DIR / file_name

        record = BackupRecord.objects.create(
            file_name=file_name, file_path=str(file_path),
            backup_type=BackupRecord.BackupType.FULL,
            status=BackupRecord.Status.IN_PROGRESS, created_by=request.user,
        )
        try:
            buffer = io.StringIO()
            call_command(
                "dumpdata", *BACKUP_APP_LABELS,
                indent=2, stdout=buffer, natural_foreign=True, natural_primary=False,
            )
            content = buffer.getvalue()
            file_path.write_text(content, encoding="utf-8")

            record.file_size_bytes = file_path.stat().st_size
            record.status = BackupRecord.Status.SUCCESS
            record.save()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Backup failed")
            record.status = BackupRecord.Status.FAILED
            record.error_message = str(exc)
            record.save()
            return error_response(f"Backup failed: {exc}", status=500)

        return success_response(
            data=BackupRecordSerializer(record).data,
            message="Backup created successfully.",
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        record = self.get_object()
        try:
            return FileResponse(
                open(record.file_path, "rb"), as_attachment=True, filename=record.file_name
            )
        except FileNotFoundError:
            return error_response("Backup file no longer exists on disk.", status=404)

    def destroy(self, request, *args, **kwargs):
        record = self.get_object()
        try:
            path = settings.BACKUP_DIR / record.file_name
            if path.exists():
                path.unlink()
        except OSError as exc:
            logger.warning("Could not delete backup file: %s", exc)
        record.delete()
        return success_response(message="Backup deleted successfully.")


class RestoreView(APIView):
    """
    POST /api/backup/restore/ — Admin uploads a previously downloaded backup
    JSON fixture (or one already stored on the server) to restore data.
    THIS OVERWRITES existing rows for the restored models — confirm=true required.
    """

    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = RestoreUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uploaded_file = serializer.validated_data["file"]

        tmp_path = settings.BACKUP_DIR / f"_restore_upload_{uploaded_file.name}"
        with open(tmp_path, "wb") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        try:
            call_command("loaddata", str(tmp_path))
            RestoreRecord.objects.create(
                source_file_name=uploaded_file.name,
                status=RestoreRecord.Status.SUCCESS,
                restored_by=request.user,
            )
            return success_response(message="Database restored successfully from backup.")
        except Exception as exc:  # noqa: BLE001
            logger.exception("Restore failed")
            RestoreRecord.objects.create(
                source_file_name=uploaded_file.name,
                status=RestoreRecord.Status.FAILED,
                error_message=str(exc),
                restored_by=request.user,
            )
            return error_response(f"Restore failed: {exc}", status=500)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


class RestoreHistoryView(viewsets.ReadOnlyModelViewSet):
    """GET /api/backup/restore-history/ — audit trail of restore operations."""

    queryset = RestoreRecord.objects.select_related("restored_by").all()
    serializer_class = RestoreRecordSerializer
    permission_classes = [IsAdmin]
