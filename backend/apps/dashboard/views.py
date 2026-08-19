from datetime import timedelta

from django.db.models import Avg
from django.utils import timezone
from rest_framework.views import APIView

from apps.accounts.models import RefreshTokenAudit, User
from apps.accounts.serializers import UserSerializer
from apps.core.permissions import IsViewerOrAbove
from apps.core.responses import success_response
from apps.sensors.models import AlertLog, Sensor, SensorReading
from apps.sensors.serializers import AlertLogSerializer, SensorReadingSerializer
from apps.stations.models import Station
from apps.stations.serializers import StationSerializer

# A station/sensor is considered "online" if it has reported a reading
# within this window; otherwise it's shown as Offline on the dashboard.
ONLINE_WINDOW_MINUTES = 15


class DashboardSummaryView(APIView):
    """
    GET /api/dashboard/summary/

    Single aggregated payload that drives the whole dashboard: overall stats
    cards, live per-station readings, station/sensor health, the active
    alerts panel, a recent-activity feed, and pending user registrations —
    without the frontend needing to make many separate requests.
    """

    permission_classes = [IsViewerOrAbove]

    def get(self, request):
        now = timezone.now()
        recent_cutoff = now - timedelta(minutes=15)
        online_cutoff = now - timedelta(minutes=ONLINE_WINDOW_MINUTES)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # --- core counts -------------------------------------------------
        sensors_online = Sensor.objects.filter(status=Sensor.Status.ONLINE).count()
        sensors_total = Sensor.objects.count()
        stations_total = Station.objects.count()
        stations_active = Station.objects.filter(status=Station.Status.ACTIVE).count()

        pending_approvals = User.objects.filter(account_status=User.AccountStatus.PENDING).count()
        users_total = User.objects.count()
        users_active = User.objects.filter(is_active=True).count()

        active_alerts_qs = AlertLog.objects.filter(is_acknowledged=False)
        active_alerts = active_alerts_qs.count()
        alerts_critical = active_alerts_qs.filter(severity=AlertLog.Severity.CRITICAL).count()
        alerts_warning = active_alerts_qs.filter(severity=AlertLog.Severity.WARNING).count()

        avg_pm25 = (
            SensorReading.objects.filter(timestamp__gte=recent_cutoff).aggregate(v=Avg("pm25"))["v"]
        )
        avg_aqi_24h = (
            SensorReading.objects.filter(timestamp__gte=now - timedelta(hours=24)).aggregate(
                v=Avg("aqi_score")
            )["v"]
        )
        today_readings = SensorReading.objects.filter(timestamp__gte=today_start).count()

        latest_overall = SensorReading.objects.order_by("-timestamp").first()

        # --- live readings + health per station ---------------------------
        live_readings = []
        station_status = []
        for station in Station.objects.all().order_by("name"):
            reading = station.readings.order_by("-timestamp").first()
            is_online = bool(reading and reading.timestamp >= online_cutoff)
            station_status.append(
                {
                    "id": station.id,
                    "name": station.name,
                    "code": station.code,
                    "status": station.status,
                    "is_online": is_online,
                    "sensor_count": station.sensor_count,
                    "online_sensor_count": station.online_sensor_count,
                    "last_reading_at": reading.timestamp if reading else None,
                    "last_alert_level": reading.alert_level if reading else None,
                }
            )
            if station.status == Station.Status.ACTIVE and reading:
                live_readings.append(
                    {
                        "station": StationSerializer(station).data,
                        "reading": SensorReadingSerializer(reading).data,
                    }
                )

        # --- alerts panel (most recent unacknowledged, any severity) ------
        recent_alerts = AlertLogSerializer(
            active_alerts_qs.select_related("station")[:10], many=True
        ).data

        # --- pending registrations widget ----------------------------------
        pending_users = UserSerializer(
            User.objects.filter(account_status=User.AccountStatus.PENDING).order_by("-registration_date")[:5],
            many=True,
        ).data

        # --- recent activity feed: alerts + logins + registrations, merged --
        activity = []
        for a in AlertLog.objects.select_related("station").order_by("-created_at")[:8]:
            activity.append(
                {
                    "type": "alert",
                    "message": f"{a.station.name}: {a.message}",
                    "severity": a.severity,
                    "timestamp": a.created_at,
                }
            )
        for u in User.objects.order_by("-registration_date")[:5]:
            activity.append(
                {
                    "type": "registration",
                    "message": f"{u.full_name} registered as {u.role.title()}",
                    "severity": None,
                    "timestamp": u.registration_date,
                }
            )
        for ev in RefreshTokenAudit.objects.select_related("user").filter(
            action=RefreshTokenAudit.Action.LOGIN
        ).order_by("-created_at")[:5]:
            activity.append(
                {
                    "type": "login",
                    "message": f"{ev.user.full_name if ev.user else 'A user'} signed in",
                    "severity": None,
                    "timestamp": ev.created_at,
                }
            )
        activity.sort(key=lambda x: x["timestamp"], reverse=True)
        activity = activity[:12]

        stats = {
            "sensors_online": sensors_online,
            "sensors_total": sensors_total,
            "stations_online": sum(1 for s in station_status if s["is_online"]),
            "stations_total": stations_total,
            "stations_active": stations_active,
            "pending_approvals": pending_approvals,
            "users_total": users_total,
            "users_active": users_active,
            "active_alerts": active_alerts,
            "alerts_critical": alerts_critical,
            "alerts_warning": alerts_warning,
            "avg_pm25": round(avg_pm25, 2) if avg_pm25 is not None else None,
            "avg_aqi_24h": round(avg_aqi_24h, 1) if avg_aqi_24h is not None else None,
            "today_readings": today_readings,
        }

        data = {
            "current_aqi": latest_overall.aqi_score if latest_overall else None,
            "current_alert_level": latest_overall.alert_level if latest_overall else None,
            "current_user": UserSerializer(request.user).data,
            "stats": stats,
            "live_readings": live_readings,
            "station_status": station_status,
            "alerts": recent_alerts,
            "recent_activity": activity,
            "pending_registrations": pending_users,
            "generated_at": now,
        }
        return success_response(data=data)
