from rest_framework.views import APIView

from apps.core.permissions import IsAdmin, IsViewerOrAbove
from apps.core.responses import success_response
from apps.settings_app.models import SystemSettings
from apps.settings_app.serializers import SystemSettingsSerializer


class SystemSettingsView(APIView):
    """
    GET  /api/settings/          — any approved user can view current thresholds/prefs
    PUT|PATCH /api/settings/     — Admin only, updates the singleton settings record
    POST /api/settings/reset/    — Admin only, resets to factory defaults
    """

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [IsAdmin()]
        return [IsViewerOrAbove()]

    def get(self, request):
        return success_response(data=SystemSettingsSerializer(SystemSettings.get_solo()).data)

    def patch(self, request):
        return self._update(request, partial=True)

    def put(self, request):
        return self._update(request, partial=False)

    def _update(self, request, partial):
        instance = SystemSettings.get_solo()
        serializer = SystemSettingsSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return success_response(data=serializer.data, message="Settings updated successfully.")


class SystemSettingsResetView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        instance = SystemSettings.get_solo()
        defaults = SystemSettings()  # unsaved instance, all fields at model defaults
        for field in SystemSettings._meta.fields:
            if field.name in ("id", "created_at", "updated_at", "updated_by"):
                continue
            setattr(instance, field.name, getattr(defaults, field.name))
        instance.updated_by = request.user
        instance.save()
        return success_response(
            data=SystemSettingsSerializer(instance).data,
            message="Settings reset to factory defaults.",
        )
