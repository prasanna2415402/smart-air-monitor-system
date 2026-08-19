from rest_framework import serializers

from apps.settings_app.models import SystemSettings


class SystemSettingsSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source="updated_by.full_name", read_only=True, default=None)

    class Meta:
        model = SystemSettings
        fields = [
            "com_port", "baud_rate", "theme", "auto_refresh_enabled",
            "auto_refresh_interval_seconds",
            "co2_warning", "co2_critical", "co_warning", "co_critical",
            "voc_warning", "voc_critical", "temp_warning", "temp_critical",
            "humidity_high_warning", "humidity_high_critical",
            "humidity_low_warning", "humidity_low_critical",
            "pm25_warning", "pm25_critical", "pm10_warning", "pm10_critical",
            "aqi_warning", "aqi_critical",
            "updated_by_name", "updated_at",
        ]
        read_only_fields = ["updated_by_name", "updated_at"]

    def validate(self, attrs):
        pairs = [
            ("co2_warning", "co2_critical"), ("co_warning", "co_critical"),
            ("voc_warning", "voc_critical"), ("temp_warning", "temp_critical"),
            ("humidity_high_warning", "humidity_high_critical"),
            ("pm25_warning", "pm25_critical"), ("pm10_warning", "pm10_critical"),
            ("aqi_warning", "aqi_critical"),
        ]
        instance = self.instance
        for warn_key, crit_key in pairs:
            warn = attrs.get(warn_key, getattr(instance, warn_key, None))
            crit = attrs.get(crit_key, getattr(instance, crit_key, None))
            if warn is not None and crit is not None and warn >= crit:
                raise serializers.ValidationError(
                    {crit_key: f"{crit_key} must be greater than {warn_key}."}
                )
        return attrs
