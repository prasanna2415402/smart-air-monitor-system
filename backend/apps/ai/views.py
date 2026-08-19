import pandas as pd
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from apps.ai.predictor import _min_rows_for_ml, get_predictor_for_station
from apps.core.permissions import IsViewerOrAbove
from apps.core.responses import error_response, success_response
from apps.sensors.models import SensorReading
from apps.stations.models import Station

READING_FIELDS = [
    "timestamp", "co2_ppm", "temperature", "humidity",
    "pm25", "pm10", "pressure", "aqi_score", "alert_level",
]


def _station_dataframe(station_id: int, limit: int = 2000) -> pd.DataFrame:
    qs = (
        SensorReading.objects.filter(station_id=station_id)
        .order_by("-timestamp")
        .values(*READING_FIELDS)[:limit]
    )
    df = pd.DataFrame.from_records(list(qs))
    if not df.empty:
        df = df.sort_values("timestamp").reset_index(drop=True)
    return df


class AIPredictionView(APIView):
    """
    GET /api/ai/predict/?station=<id>

    Runs the AI/ML predictor (or its rule-based fallback, when there isn't
    enough history yet) against a station's recent readings and returns the
    predicted air-quality class, CO2 forecast, trend, anomaly flag, and
    recommended actions — the same payload shape the original Streamlit
    prototype's AI panel consumed.
    """

    permission_classes = [IsViewerOrAbove]

    def get(self, request):
        station_id = request.query_params.get("station")
        if not station_id:
            return error_response("Query param 'station' is required.", status=400)

        station = get_object_or_404(Station, pk=station_id)
        df = _station_dataframe(station.id)

        if df.empty:
            return success_response(
                data={
                    "station": station.id,
                    "predicted_class": None,
                    "confidence": None,
                    "co2_forecast": None,
                    "trend": "Stable",
                    "is_anomaly": False,
                    "method": "rule-based",
                    "recommendations": ["No readings yet for this station."],
                    "rows_available": 0,
                    "rows_required_for_ml": _min_rows_for_ml(),
                },
                message="No readings available for this station yet.",
            )

        predictor = get_predictor_for_station(station.id, df)
        current = df.iloc[-1].to_dict()
        result = predictor.predict(df, current)
        result["recommendations"] = predictor.recommendations_for_class(
            result["predicted_class"], result["trend"]
        )
        result["station"] = station.id
        result["rows_available"] = len(df)
        result["rows_required_for_ml"] = _min_rows_for_ml()
        result["model_trained"] = predictor.is_trained()
        result["cv_accuracy"] = predictor.cv_accuracy

        return success_response(data=result)


class AIModelStatusView(APIView):
    """
    GET /api/ai/status/?station=<id>

    Lightweight endpoint for a dashboard badge: whether the ML models are
    trained yet for this station, and how many readings are needed.
    """

    permission_classes = [IsViewerOrAbove]

    def get(self, request):
        station_id = request.query_params.get("station")
        if not station_id:
            return error_response("Query param 'station' is required.", status=400)

        station = get_object_or_404(Station, pk=station_id)
        rows = SensorReading.objects.filter(station_id=station.id).count()
        min_rows = _min_rows_for_ml()

        return success_response(
            data={
                "station": station.id,
                "rows_available": rows,
                "rows_required_for_ml": min_rows,
                "ml_ready": rows >= min_rows,
            }
        )
