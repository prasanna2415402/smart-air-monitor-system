"""
AQI scoring, alert classification, and threshold-breach checks — ported
1:1 from the original Streamlit prototype's alerts.py so behaviour stays
identical, now used by the ingest endpoint to populate aqi_score,
alert_level, and AlertLog rows automatically.
"""

DEFAULT_THRESHOLDS = {
    "co2_warning": 1000, "co2_critical": 1500,
    "co_warning": 9, "co_critical": 35,
    "voc_warning": 150, "voc_critical": 300,
    "temp_warning": 28, "temp_critical": 35,
    "hum_high_warning": 70, "hum_high_critical": 85,
    "hum_low_warning": 30, "hum_low_critical": 20,
    "pm25_warning": 25, "pm25_critical": 75,
    "pm10_warning": 50, "pm10_critical": 150,
    "aqi_warning": 100, "aqi_critical": 150,
}


def calculate_aqi(data: dict) -> float:
    """Simplified weighted AQI (0-500 scale)."""
    co2_norm = min(data["co2_ppm"] / 2000, 1.0) * 100
    co_norm = min(data.get("co_ppm", 0) / 50, 1.0) * 100
    voc_norm = min(data.get("voc_index", 0) / 500, 1.0) * 100
    pm25_norm = min(data["pm25"] / 250, 1.0) * 100
    pm10_norm = min(data["pm10"] / 350, 1.0) * 100
    hum_penalty = abs(data["humidity"] - 50) / 50 * 30
    return round(
        co2_norm * 0.30
        + pm25_norm * 0.30
        + pm10_norm * 0.15
        + co_norm * 0.10
        + voc_norm * 0.10
        + hum_penalty * 0.05,
        1,
    )


def classify_alert_level(aqi: float) -> str:
    if aqi < 50:
        return "GOOD"
    elif aqi < 100:
        return "MODERATE"
    elif aqi < 150:
        return "POOR"
    elif aqi < 200:
        return "VERY_POOR"
    return "HAZARDOUS"


def check_thresholds(data: dict, thresholds: dict = None):
    """Returns a list of dicts: [{parameter, severity, message, recommendation}, ...]."""
    t = thresholds or DEFAULT_THRESHOLDS
    results = []

    co2 = data["co2_ppm"]
    if co2 > t["co2_critical"]:
        results.append({
            "parameter": "CO2", "severity": "CRITICAL",
            "message": f"CO2 CRITICAL ({co2:.0f} PPM)",
            "recommendation": "Evacuate or open windows immediately — ventilate urgently.",
        })
    elif co2 > t["co2_warning"]:
        results.append({
            "parameter": "CO2", "severity": "WARNING",
            "message": f"CO2 ELEVATED ({co2:.0f} PPM)",
            "recommendation": "Open windows or turn on ventilation to increase fresh air.",
        })

    co = data.get("co_ppm", 0)
    if co > t.get("co_critical", 35):
        results.append({
            "parameter": "CO", "severity": "CRITICAL",
            "message": f"CO CRITICAL ({co:.1f} PPM)",
            "recommendation": "Evacuate the area and ventilate immediately — carbon monoxide risk.",
        })
    elif co > t.get("co_warning", 9):
        results.append({
            "parameter": "CO", "severity": "WARNING",
            "message": f"CO ELEVATED ({co:.1f} PPM)",
            "recommendation": "Check combustion equipment and increase ventilation.",
        })

    voc = data.get("voc_index", 0)
    if voc > t.get("voc_critical", 300):
        results.append({
            "parameter": "VOC", "severity": "CRITICAL",
            "message": f"VOC HAZARDOUS ({voc:.0f} index)",
            "recommendation": "Ventilate immediately and identify the VOC source (solvents, fumes).",
        })
    elif voc > t.get("voc_warning", 150):
        results.append({
            "parameter": "VOC", "severity": "WARNING",
            "message": f"VOC ELEVATED ({voc:.0f} index)",
            "recommendation": "Increase fresh-air exchange; avoid strong solvents or fumes nearby.",
        })

    pm25 = data["pm25"]
    if pm25 > t["pm25_critical"]:
        results.append({
            "parameter": "PM2.5", "severity": "CRITICAL",
            "message": f"PM2.5 HAZARDOUS ({pm25:.1f} µg/m³)",
            "recommendation": "Stay indoors, close windows, run an air purifier immediately.",
        })
    elif pm25 > t["pm25_warning"]:
        results.append({
            "parameter": "PM2.5", "severity": "WARNING",
            "message": f"PM2.5 ELEVATED ({pm25:.1f} µg/m³)",
            "recommendation": "Avoid strenuous activity; consider an air purifier.",
        })

    pm10 = data["pm10"]
    if pm10 > t["pm10_critical"]:
        results.append({
            "parameter": "PM10", "severity": "CRITICAL",
            "message": f"PM10 HAZARDOUS ({pm10:.1f} µg/m³)",
            "recommendation": "Close windows to keep out coarse dust; use HVAC filtration.",
        })
    elif pm10 > t["pm10_warning"]:
        results.append({
            "parameter": "PM10", "severity": "WARNING",
            "message": f"PM10 ELEVATED ({pm10:.1f} µg/m³)",
            "recommendation": "",
        })

    hum = data["humidity"]
    if hum > t["hum_high_critical"]:
        results.append({
            "parameter": "HUMIDITY", "severity": "CRITICAL",
            "message": f"HUMIDITY CRITICAL ({hum:.0f}%)",
            "recommendation": "Run a dehumidifier immediately — mold risk is severe.",
        })
    elif hum > t["hum_high_warning"]:
        results.append({
            "parameter": "HUMIDITY", "severity": "WARNING",
            "message": f"HIGH HUMIDITY ({hum:.0f}%)",
            "recommendation": "Run a dehumidifier or increase air circulation.",
        })
    elif hum < t["hum_low_critical"]:
        results.append({
            "parameter": "HUMIDITY", "severity": "CRITICAL",
            "message": f"HUMIDITY TOO LOW ({hum:.0f}%)",
            "recommendation": "Use a humidifier; very dry air irritates skin and airways.",
        })
    elif hum < t["hum_low_warning"]:
        results.append({
            "parameter": "HUMIDITY", "severity": "WARNING",
            "message": f"LOW HUMIDITY ({hum:.0f}%)",
            "recommendation": "Consider a humidifier if discomfort persists.",
        })

    temp = data["temperature"]
    if temp > t["temp_critical"]:
        results.append({
            "parameter": "TEMPERATURE", "severity": "CRITICAL",
            "message": f"TEMPERATURE CRITICAL ({temp:.1f}°C)",
            "recommendation": "Increase cooling/ventilation immediately.",
        })
    elif temp > t["temp_warning"]:
        results.append({
            "parameter": "TEMPERATURE", "severity": "WARNING",
            "message": f"TEMPERATURE ELEVATED ({temp:.1f}°C)",
            "recommendation": "Consider increasing ventilation or AC.",
        })

    return results


def fan_hysteresis(current_fan_state: bool, aqi: float, thresholds: dict = None) -> bool:
    """Simple on/off hysteresis: turn fan on above 'warning', off below 'good'."""
    t = thresholds or DEFAULT_THRESHOLDS
    if aqi >= t["aqi_warning"]:
        return True
    if aqi < 50:
        return False
    return current_fan_state
