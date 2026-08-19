"""
apps/ai/predictor.py
---------------------
AI/ML Prediction engine — ported from the original standalone prototype's
`ai_predictor.py` (report Section 15) into the Django backend.

- RandomForestClassifier    -> air quality class (GOOD/MODERATE/POOR/VERY_POOR/HAZARDOUS)
- GradientBoostingRegressor -> CO2 forecast ~30 minutes ahead
- IsolationForest           -> anomaly / sensor-fault detection

Behaviour is unchanged from the prototype: until a station has collected
`AI_MIN_READINGS_FOR_ML` (settings.py, default 60) readings, predictions
fall back to transparent rule-based / linear-trend logic so the dashboard
is never empty or broken on a fresh install. Once enough history exists,
models are trained lazily on first request and cached in-process per
station, keyed on the row count last trained on.
"""

from __future__ import annotations

import threading

import numpy as np
import pandas as pd
from django.conf import settings
from sklearn.ensemble import GradientBoostingRegressor, IsolationForest, RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from apps.sensors.alerts import calculate_aqi, classify_alert_level

CLASS_ORDER = ["GOOD", "MODERATE", "POOR", "VERY_POOR", "HAZARDOUS"]

FEATURE_COLS = [
    "co2_ppm", "co2_delta_5m", "co2_rolling_mean_15m",
    "pm25", "pm25_delta_5m", "hour_of_day",
    "humidity", "temperature", "aqi_prev",
]


def _min_rows_for_ml() -> int:
    return getattr(settings, "AI_MIN_READINGS_FOR_ML", 60)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Feature engineering pipeline described in report Section 15."""
    df = df.sort_values("timestamp").copy()
    df["co2_delta_5m"] = df["co2_ppm"].diff(periods=min(5, max(len(df) - 1, 1))).fillna(0)
    df["co2_rolling_mean_15m"] = df["co2_ppm"].rolling(15, min_periods=1).mean()
    df["pm25_delta_5m"] = df["pm25"].diff(periods=min(5, max(len(df) - 1, 1))).fillna(0)
    df["hour_of_day"] = pd.to_datetime(df["timestamp"]).dt.hour
    df["aqi_prev"] = df["aqi_score"].shift(1).fillna(df["aqi_score"])
    return df


class AIPredictor:
    """A single station's trained (or not-yet-trained) model bundle."""

    def __init__(self):
        self.classifier: Pipeline | None = None
        self.regressor: GradientBoostingRegressor | None = None
        self.anomaly_model: IsolationForest | None = None
        self.trained_rows = 0
        self.cv_accuracy = None

    def is_trained(self) -> bool:
        return self.classifier is not None

    def train(self, df: pd.DataFrame) -> bool:
        if len(df) < _min_rows_for_ml():
            return False

        feat_df = build_features(df)
        X = feat_df[FEATURE_COLS].fillna(0)
        y = feat_df["alert_level"].fillna("GOOD")

        # Need at least 2 classes to fit a classifier meaningfully.
        if y.nunique() >= 2:
            pipe = Pipeline([
                ("scaler", StandardScaler()),
                ("model", RandomForestClassifier(n_estimators=150, random_state=42)),
            ])
            pipe.fit(X, y)
            self.classifier = pipe
            try:
                from sklearn.model_selection import cross_val_score
                scores = cross_val_score(pipe, X, y, cv=min(5, y.value_counts().min()))
                self.cv_accuracy = float(np.mean(scores))
            except Exception:
                self.cv_accuracy = None
        else:
            self.classifier = None

        # Regressor: predict CO2 ~30 min (6 steps) ahead.
        horizon = min(6, max(1, len(feat_df) // 10))
        target = feat_df["co2_ppm"].shift(-horizon)
        train_mask = target.notna()
        if train_mask.sum() >= 20:
            reg = GradientBoostingRegressor(random_state=42)
            reg.fit(X[train_mask], target[train_mask])
            self.regressor = reg
        else:
            self.regressor = None

        # Anomaly detector.
        try:
            iso = IsolationForest(contamination=0.05, random_state=42)
            iso.fit(X)
            self.anomaly_model = iso
        except Exception:
            self.anomaly_model = None

        self.trained_rows = len(df)
        return True

    def predict(self, df: pd.DataFrame, current: dict) -> dict:
        """
        Returns a dict with keys: predicted_class, confidence, co2_forecast,
        trend, is_anomaly, method ('ml' or 'rule-based').
        """
        result = {
            "predicted_class": current.get(
                "alert_level",
                classify_alert_level(current.get("aqi_score") or calculate_aqi(current)),
            ),
            "confidence": None,
            "co2_forecast": None,
            "trend": "Stable",
            "is_anomaly": False,
            "method": "rule-based",
        }

        if len(df) < 5:
            return result

        feat_df = build_features(df)
        latest_feat = feat_df[FEATURE_COLS].fillna(0).iloc[[-1]]

        # --- Trend (always available, even without a trained model) ---
        recent = df["co2_ppm"].tail(10).values
        if len(recent) >= 2:
            slope = np.polyfit(range(len(recent)), recent, 1)[0]
            if slope > 3:
                result["trend"] = "Rapidly Increasing"
            elif slope > 0.5:
                result["trend"] = "Increasing"
            elif slope < -3:
                result["trend"] = "Rapidly Decreasing"
            elif slope < -0.5:
                result["trend"] = "Decreasing"
            else:
                result["trend"] = "Stable"
            result["co2_forecast"] = round(float(recent[-1] + slope * 6), 1)

        # --- Classifier ---
        if self.classifier is not None:
            try:
                pred = self.classifier.predict(latest_feat)[0]
                proba = self.classifier.predict_proba(latest_feat).max()
                result["predicted_class"] = pred
                result["confidence"] = round(float(proba) * 100, 1)
                result["method"] = "ml"
            except Exception:
                pass

        # --- Regressor (overrides linear fallback if available) ---
        if self.regressor is not None:
            try:
                forecast = self.regressor.predict(latest_feat)[0]
                result["co2_forecast"] = round(float(forecast), 1)
                result["method"] = "ml"
            except Exception:
                pass

        # --- Anomaly detection ---
        if self.anomaly_model is not None:
            try:
                flag = self.anomaly_model.predict(latest_feat)[0]
                result["is_anomaly"] = bool(flag == -1)
            except Exception:
                pass

        return result

    @staticmethod
    def recommendations_for_class(predicted_class: str, trend: str) -> list:
        recs = {
            "GOOD": ["Air quality is excellent. No action needed."],
            "MODERATE": ["Monitor conditions; consider light ventilation."],
            "POOR": [
                "Open a window or run ventilation soon.",
                "Reduce occupancy or activity if possible.",
            ],
            "VERY_POOR": [
                "Ventilate immediately.",
                "Consider reducing occupancy.",
                "Run an air purifier if particulate matter is high.",
            ],
            "HAZARDOUS": [
                "Evacuate or ventilate immediately.",
                "Avoid the space until levels recover.",
            ],
        }.get(predicted_class, ["Monitor conditions."])
        if "Increasing" in trend:
            recs.append("Trend is worsening — act proactively rather than waiting.")
        return recs


# ---------------------------------------------------------------- REGISTRY
# One AIPredictor instance is kept in-process per station so models aren't
# retrained on every single request. Re-trained automatically whenever the
# station's reading count has grown meaningfully since the last fit.
_lock = threading.Lock()
_registry: dict[int, AIPredictor] = {}

RETRAIN_EVERY_N_NEW_ROWS = 20


def get_predictor_for_station(station_id: int, df: pd.DataFrame) -> AIPredictor:
    with _lock:
        predictor = _registry.get(station_id)
        if predictor is None:
            predictor = AIPredictor()
            _registry[station_id] = predictor

        rows = len(df)
        needs_initial_fit = not predictor.is_trained() and rows >= _min_rows_for_ml()
        needs_refresh = predictor.is_trained() and (rows - predictor.trained_rows) >= RETRAIN_EVERY_N_NEW_ROWS
        if needs_initial_fit or needs_refresh:
            predictor.train(df)

        return predictor
