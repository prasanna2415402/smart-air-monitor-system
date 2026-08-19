from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from apps.core.permissions import IsOperatorOrAdmin, IsViewerOrAbove
from apps.core.responses import success_response
from apps.stations.models import Station
from apps.stations.serializers import StationSerializer


class StationViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for monitoring stations/zones.
    Read: any approved authenticated user (Viewer/Operator/Admin).
    Write: Operator or Admin only.
    """

    queryset = Station.objects.select_related("created_by").all()
    serializer_class = StationSerializer
    permission_classes = [IsViewerOrAbove, IsOperatorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status"]
    search_fields = ["name", "code", "location"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(
            data=serializer.data, message="Station created successfully.", status=201
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Station updated successfully.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(message="Station deleted successfully.")
