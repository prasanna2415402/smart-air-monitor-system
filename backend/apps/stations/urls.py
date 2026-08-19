from rest_framework.routers import DefaultRouter

from apps.stations.views import StationViewSet

router = DefaultRouter()
router.register("", StationViewSet, basename="station")

urlpatterns = router.urls
