from rest_framework.routers import DefaultRouter

from apps.backup.views import BackupViewSet, RestoreHistoryView, RestoreView
from django.urls import path, include

router = DefaultRouter()
router.register("restore-history", RestoreHistoryView, basename="restore-history")
router.register("", BackupViewSet, basename="backup")

urlpatterns = [
    path("restore/", RestoreView.as_view(), name="backup-restore"),
    path("", include(router.urls)),
]
