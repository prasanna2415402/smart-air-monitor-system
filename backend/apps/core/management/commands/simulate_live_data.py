"""
Generates new SensorReading rows for every active station, using the exact
same AQI/alert-classification engine as the real ESP32 ingest endpoint
(apps.sensors.alerts). This stands in for real hardware / the ESP32
firmware described in docs/esp32_firmware.ino so the dashboard has genuine,
constantly-refreshing data to display instead of static seed data.

Usage:
    # one-shot: push a single new reading per active station, then exit
    python manage.py simulate_live_data --once

    # keep running, pushing new readings every 10 seconds (Ctrl+C to stop)
    python manage.py simulate_live_data --interval 10
"""
import random
import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.sensors import alerts as alert_engine
from apps.sensors.models import AlertLog, SensorReading
from apps.settings_app.models import SystemSettings
from apps.stations.models import Station


class Command(BaseCommand):
    help = "Simulate a live data feed by periodically ingesting new sensor readings for every active station."

    def add_arguments(self, parser):
        parser.add_argument("--interval", type=int, default=10, help="Seconds between ticks (default: 10).")
        parser.add_argument("--once", action="store_true", help="Push a single reading per station, then exit.")

    def handle(self, *args, **options):
        interval = options["interval"]
        once = options["once"]

        stations = list(Station.objects.filter(status=Station.Status.ACTIVE))
        if not stations:
            self.stdout.write(self.style.WARNING("No active stations found. Run seed_data first."))
            return

        try:
            while True:
                thresholds = SystemSettings.get_solo().as_thresholds_dict()
                for station in stations:
                    reading, alerts_raised = self._tick(station, thresholds)
                    self.stdout.write(
                        f"[{timezone.localtime():%H:%M:%S}] {station.code}: "
                        f"AQI={reading.aqi_score} ({reading.alert_level}), "
                        f"{alerts_raised} alert(s) raised"
                    )
                if once:
                    break
                time.sleep(interval)
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("Stopped."))

    def _tick(self, station, thresholds):
        last = station.readings.order_by("-timestamp").first()

        def drift(prev, lo, hi, spread):
            base = prev if prev is not None else random.uniform(lo, hi)
            return max(lo, min(hi, base + random.uniform(-spread, spread)))

        data = {
            "co2_ppm": drift(last.co2_ppm if last else None, 350, 1600, 60),
            "co_ppm": drift(last.co_ppm if last else None, 0.2, 40, 3),
            "voc_index": drift(last.voc_index if last else None, 10, 350, 20),
            "temperature": drift(last.temperature if last else None, 17, 32, 0.8),
            "humidity": drift(last.humidity if last else None, 25, 80, 3),
            "pm25": drift(last.pm25 if last else None, 2, 85, 6),
            "pm10": drift(last.pm10 if last else None, 5, 150, 10),
            "pressure": drift(last.pressure if last else None, 1000, 1025, 1),
        }

        aqi = alert_engine.calculate_aqi(data)
        level = alert_engine.classify_alert_level(aqi)
        fan_state = alert_engine.fan_hysteresis(last.fan_state if last else False, aqi, thresholds)

        reading = SensorReading.objects.create(
            station=station, timestamp=timezone.now(), aqi_score=aqi, alert_level=level,
            fan_state=fan_state, **data,
        )

        breaches = alert_engine.check_thresholds(data, thresholds)
        AlertLog.objects.bulk_create(
            [
                AlertLog(
                    station=station, reading=reading, parameter=b["parameter"],
                    severity=b["severity"], message=b["message"], recommendation=b["recommendation"],
                )
                for b in breaches
            ]
        )
        return reading, len(breaches)
