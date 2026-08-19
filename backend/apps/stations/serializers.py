from rest_framework import serializers

from apps.stations.models import Station


class StationSerializer(serializers.ModelSerializer):
    sensor_count = serializers.IntegerField(read_only=True)
    online_sensor_count = serializers.IntegerField(read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = Station
        fields = [
            "id", "name", "code", "location", "description", "status",
            "latitude", "longitude", "sensor_count", "online_sensor_count",
            "created_by", "created_by_name", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def validate_code(self, value):
        return value.strip().upper()
