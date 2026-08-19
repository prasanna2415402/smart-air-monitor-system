import os
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.sensors import alerts as alert_engine
from apps.sensors.models import AlertLog, Sensor, SensorReading
from apps.settings_app.models import SystemSettings
from apps.stations.models import Station


class Command(BaseCommand):
    help = "Seed the database with a superuser, sample users, stations, sensors, and historical readings."

    def add_arguments(self, parser):
        parser.add_argument(
            "--readings", type=int, default=200,
            help="Number of historical sensor readings to generate per station (default: 200).",
        )
        parser.add_argument(
            "--flush", action="store_true",
            help="Delete existing seeded data before re-seeding.",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Flushing existing sample data...")
            SensorReading.objects.all().delete()
            AlertLog.objects.all().delete()
            Sensor.objects.all().delete()
            Station.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        self._create_superuser()
        admin = User.objects.filter(is_superuser=True).first()
        self._create_sample_users(admin)
        stations = self._create_stations(admin)
        sensors = self._create_sensors(stations, admin)
        self._create_readings(stations, sensors, options["readings"])
        SystemSettings.get_solo()

        self.stdout.write(self.style.SUCCESS("Sample data seeded successfully."))

    # ------------------------------------------------------------------
    def _create_superuser(self):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@smartair.com")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "Admin@12345")

        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Superuser '{username}' already exists, skipping.")
            return

        User.objects.create_superuser(
            username=username, email=email, password=password,
            full_name="Alex Supervisor", mobile_number="+1-555-0100", employee_id="EMP-0001",
        )
        self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}' / password '{password}'"))

    def _create_sample_users(self, admin):
        sample_users = [
            dict(username="maria.lopez", email="maria.l@acme.com", full_name="Maria Lopez",
                 role=User.Role.OPERATOR, mobile_number="+1-555-0111", account_status=User.AccountStatus.PENDING, is_active=False),
            dict(username="tom.reed", email="tom.reed@acme.com", full_name="Thomas Reed",
                 role=User.Role.VIEWER, mobile_number="+1-555-0112", account_status=User.AccountStatus.PENDING, is_active=False),
            dict(username="priya.sharma", email="priya.s@acme.com", full_name="Priya Sharma",
                 role=User.Role.OPERATOR, mobile_number="+1-555-0113", account_status=User.AccountStatus.PENDING, is_active=False),
            dict(username="james.operator", email="james.op@acme.com", full_name="James Carter",
                 role=User.Role.OPERATOR, mobile_number="+1-555-0114", account_status=User.AccountStatus.APPROVED, is_active=True),
            dict(username="sara.viewer", email="sara.v@acme.com", full_name="Sara Kim",
                 role=User.Role.VIEWER, mobile_number="+1-555-0115", account_status=User.AccountStatus.APPROVED, is_active=True),
        ]
        created = 0
        for data in sample_users:
            if User.objects.filter(username=data["username"]).exists():
                continue
            status = data.pop("account_status")
            active = data.pop("is_active")
            user = User(**data)
            user.set_password("Passw0rd!")
            user.account_status = status
            user.is_active = active
            if status == User.AccountStatus.APPROVED:
                user.approved_by = admin
                user.approved_at = timezone.now()
            user.save()
            created += 1
        self.stdout.write(f"Created {created} sample user(s) (password: 'Passw0rd!').")

    def _create_stations(self, admin):
        station_defs = [
            dict(name="Zone A - Production", code="ZONE-A", location="Building 1, Floor 2"),
            dict(name="Zone B - Warehouse", code="ZONE-B", location="Building 2, Ground Floor"),
            dict(name="Zone C - Lab", code="ZONE-C", location="Building 1, Floor 3"),
        ]
        stations = []
        for data in station_defs:
            station, _ = Station.objects.get_or_create(
                code=data["code"], defaults={**data, "created_by": admin}
            )
            stations.append(station)
        self.stdout.write(f"Ensured {len(stations)} station(s) exist.")
        return stations

    def _create_sensors(self, stations, admin):
        sensor_map = {}
        for station in stations:
            sensors = []
            for sensor_type in ["CO2", "CO", "VOC", "TEMPERATURE", "HUMIDITY", "PM25", "PM10", "PRESSURE"]:
                serial = f"{station.code}-{sensor_type}"
                sensor, _ = Sensor.objects.get_or_create(
                    serial_number=serial,
                    defaults=dict(
                        station=station, name=f"{sensor_type.title()} Sensor",
                        sensor_type=sensor_type, status=Sensor.Status.ONLINE, created_by=admin,
                    ),
                )
                sensors.append(sensor)
            sensor_map[station.id] = sensors
        self.stdout.write("Ensured sensors exist for every station.")
        return sensor_map

    def _create_readings(self, stations, sensor_map, n):
        thresholds = alert_engine.DEFAULT_THRESHOLDS
        now = timezone.now()
        total_created = 0
        total_alerts = 0
        for station in stations:
            if station.readings.exists():
                continue
            objs = []
            alert_objs = []
            for i in range(n):
                # Space most readings 5 minutes apart, but keep the last few
                # within the last several minutes so the dashboard shows the
                # station as "Online" right after seeding.
                if i >= n - 3:
                    ts_offset = timedelta(minutes=(n - 1 - i) * 2)
                else:
                    ts_offset = timedelta(minutes=(n - i) * 5)

                spike = random.random() < 0.06  # ~6% of historical readings breach a threshold
                co2 = random.uniform(1100, 1800) if spike else random.uniform(350, 900)
                co = random.uniform(10, 45) if spike else random.uniform(0.2, 6)
                voc = random.uniform(180, 400) if spike else random.uniform(10, 120)
                temp = random.uniform(18, 26)
                hum = random.uniform(35, 65)
                pm25 = random.uniform(30, 90) if spike else random.uniform(2, 22)
                pm10 = random.uniform(60, 160) if spike else random.uniform(5, 45)
                pressure = random.uniform(1005, 1020)
                data = {
                    "co2_ppm": co2, "co_ppm": co, "voc_index": voc,
                    "temperature": temp, "humidity": hum, "pm25": pm25, "pm10": pm10, "pressure": pressure,
                }
                aqi = alert_engine.calculate_aqi(data)
                level = alert_engine.classify_alert_level(aqi)
                reading = SensorReading(
                    station=station, timestamp=now - ts_offset,
                    co2_ppm=co2, co_ppm=co, voc_index=voc,
                    temperature=temp, humidity=hum, pm25=pm25, pm10=pm10, pressure=pressure,
                    aqi_score=aqi, alert_level=level, fan_state=aqi >= thresholds["aqi_warning"],
                )
                objs.append(reading)

                breaches = alert_engine.check_thresholds(data, thresholds)
                for b in breaches:
                    alert_objs.append((reading, b))

            SensorReading.objects.bulk_create(objs)
            total_created += len(objs)

            # AlertLog rows reference the saved reading's pk, so create them
            # in a second pass now that bulk_create has assigned ids (SQLite
            # returns pks from bulk_create, but keep this explicit/portable).
            log_objs = [
                AlertLog(
                    station=station, reading=reading, parameter=b["parameter"],
                    severity=b["severity"], message=b["message"], recommendation=b["recommendation"],
                    is_acknowledged=random.random() < 0.5,
                )
                for reading, b in alert_objs
            ]
            AlertLog.objects.bulk_create(log_objs)
            total_alerts += len(log_objs)

        self.stdout.write(f"Created {total_created} historical reading(s) and {total_alerts} alert log(s).")
