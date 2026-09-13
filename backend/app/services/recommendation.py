"""
app/services/recommendation.py
--------------------------------
Rule-based agronomic advisory engine for AgriSmart AI.

This module computes:
  1. Irrigation recommendations  — whether to irrigate today, best method,
     and a 3-day rolling schedule.
  2. Sustainability score        — a composite 0–100 metric.
  3. Weather risk analysis       — mock forecast with crop-specific risk flags.

Design philosophy
-----------------
• Pure functions with no external I/O — easy to unit-test.
• All thresholds are named constants at module level — easy to tune.
• Annotated with TODO markers where a real data-science model or external
  API call would replace the rule logic.
"""

from __future__ import annotations

import math
import random
from datetime import date, timedelta
from typing import Any, Dict, List, Tuple

from app.schemas.advisory import (
    AdvisoryRequest,
    AdvisoryResponse,
    IrrigationMethod,
    IrrigationScheduleItem,
    WeatherRiskRequest,
    WeatherRiskResponse,
)

# =========================================================================== #
#  Agronomic constants
# =========================================================================== #

# Optimal moisture windows (%) per crop growth stage
STAGE_MOISTURE_OPTIMAL: Dict[str, Tuple[float, float]] = {
    "germination": (60.0, 80.0),
    "seedling":    (55.0, 75.0),
    "vegetative":  (50.0, 70.0),
    "flowering":   (55.0, 70.0),
    "fruiting":    (50.0, 65.0),
    "harvest":     (40.0, 55.0),
}

# Water volume (L/m²) required per stage when irrigating
STAGE_WATER_VOLUME: Dict[str, float] = {
    "germination": 4.0,
    "seedling":    3.5,
    "vegetative":  3.0,
    "flowering":   4.0,
    "fruiting":    3.5,
    "harvest":     2.0,
}

# Optimal soil pH range per crop (approximate)
CROP_PH_OPTIMAL: Dict[str, Tuple[float, float]] = {
    "tomato":   (6.0, 6.8),
    "wheat":    (6.0, 7.0),
    "rice":     (5.5, 6.5),
    "paddy":    (5.5, 6.5),
    "maize":    (5.8, 7.0),
    "corn":     (5.8, 7.0),
    "potato":   (4.8, 6.0),
    "cotton":   (5.8, 7.0),
    "soybean":  (6.0, 7.0),
    "groundnut":(5.9, 7.0),
    "sugarcane":(6.0, 7.5),
    "default":  (5.5, 7.5),
}

# Irrigation method scores per soil type (higher = better fit)
SOIL_METHOD_SCORES: Dict[str, Dict[str, float]] = {
    "clay":   {"drip": 0.9, "sprinkler": 0.6, "flood": 0.4, "furrow": 0.7, "none": 0.0},
    "sandy":  {"drip": 1.0, "sprinkler": 0.7, "flood": 0.3, "furrow": 0.5, "none": 0.0},
    "loamy":  {"drip": 0.9, "sprinkler": 0.8, "flood": 0.6, "furrow": 0.7, "none": 0.0},
    "silty":  {"drip": 0.8, "sprinkler": 0.7, "flood": 0.5, "furrow": 0.6, "none": 0.0},
    "peaty":  {"drip": 0.8, "sprinkler": 0.6, "flood": 0.3, "furrow": 0.4, "none": 0.0},
    "chalky": {"drip": 0.9, "sprinkler": 0.7, "flood": 0.4, "furrow": 0.6, "none": 0.0},
    "saline": {"drip": 1.0, "sprinkler": 0.4, "flood": 0.2, "furrow": 0.5, "none": 0.0},
}

# Temperature stress thresholds (°C)
HEAT_STRESS_THRESHOLD = 35.0
COLD_STRESS_THRESHOLD = 5.0

# Rain probability threshold above which irrigation is skipped
RAIN_SKIP_THRESHOLD = 0.70


# =========================================================================== #
#  Helper functions
# =========================================================================== #


def _optimal_moisture_range(stage: str) -> Tuple[float, float]:
    return STAGE_MOISTURE_OPTIMAL.get(stage, (50.0, 70.0))


def _crop_ph_range(crop_name: str) -> Tuple[float, float]:
    return CROP_PH_OPTIMAL.get(crop_name.lower(), CROP_PH_OPTIMAL["default"])


def _best_irrigation_method(soil_type: str, rain_prob: float) -> IrrigationMethod:
    """Pick the irrigation method with the highest soil-fit score."""
    scores = SOIL_METHOD_SCORES.get(soil_type.lower(), SOIL_METHOD_SCORES["loamy"])
    methods = [m for m in scores if m != "none"]
    best = max(methods, key=lambda m: scores[m])
    if rain_prob > RAIN_SKIP_THRESHOLD:
        return IrrigationMethod.NONE
    return IrrigationMethod(best)


def _compute_sustainability_score(req: AdvisoryRequest) -> float:
    """
    Compute a composite sustainability score in [0, 100].

    Sub-scores (each 0–1):
      • water_efficiency  — penalises over-irrigation and high rain_prob overlap
      • soil_health       — based on pH proximity to crop optimum
      • method_fit        — irrigation method suitability for soil type
      • temperature_fit   — penalty for heat / cold stress
    """
    # Water efficiency
    lo, hi = _optimal_moisture_range(req.crop_stage.value)
    moisture_gap = max(0.0, lo - req.moisture)  # deficit
    moisture_excess = max(0.0, req.moisture - hi)  # excess
    water_penalty = (moisture_gap + moisture_excess) / 100.0
    rain_bonus = req.rain_prob * 0.1  # reward for rain reducing irrigation need
    water_score = max(0.0, 1.0 - water_penalty + rain_bonus)

    # Soil pH health
    ph_lo, ph_hi = _crop_ph_range(req.crop_name)
    ph_mid = (ph_lo + ph_hi) / 2
    ph_dev = abs(req.ph - ph_mid) / ((ph_hi - ph_lo) / 2 + 0.01)
    soil_score = max(0.0, 1.0 - ph_dev * 0.5)

    # Irrigation method fit
    scores = SOIL_METHOD_SCORES.get(req.soil_type.value, SOIL_METHOD_SCORES["loamy"])
    method_val = req.current_irrigation_method.value if req.current_irrigation_method else "none"
    method_score = scores.get(method_val, 0.5)

    # Temperature fit (penalise extremes)
    if req.temperature >= HEAT_STRESS_THRESHOLD:
        temp_score = max(0.0, 1.0 - (req.temperature - HEAT_STRESS_THRESHOLD) / 20.0)
    elif req.temperature <= COLD_STRESS_THRESHOLD:
        temp_score = max(0.0, 1.0 - (COLD_STRESS_THRESHOLD - req.temperature) / 20.0)
    else:
        temp_score = 1.0

    # Weighted composite
    composite = (
        water_score  * 0.35
        + soil_score  * 0.30
        + method_score * 0.20
        + temp_score  * 0.15
    )
    return round(min(100.0, composite * 100.0), 1)


def _sustainability_rating(score: float) -> str:
    if score >= 80:
        return "Excellent"
    if score >= 60:
        return "Good"
    if score >= 40:
        return "Fair"
    return "Poor"


def _build_irrigation_schedule(
    req: AdvisoryRequest,
    should_irrigate_today: bool,
    method: IrrigationMethod,
) -> List[IrrigationScheduleItem]:
    """Generate a 3-day ahead irrigation schedule."""
    schedule: List[IrrigationScheduleItem] = []
    base_volume = STAGE_WATER_VOLUME.get(req.crop_stage.value, 3.0)

    for day_offset in range(3):
        # Simulate declining rain probability over forecast window
        simulated_rain = req.rain_prob * max(0.0, 1.0 - day_offset * 0.15)
        irrigate = should_irrigate_today if day_offset == 0 else simulated_rain < RAIN_SKIP_THRESHOLD

        if not irrigate:
            schedule.append(IrrigationScheduleItem(
                day_offset=day_offset,
                duration_minutes=0,
                water_volume_liters_per_sqm=0.0,
                notes=f"Skip — rain probability {simulated_rain:.0%} exceeds threshold.",
            ))
        else:
            # Adjust volume for temperature (hot days need more water)
            temp_factor = 1.0 + max(0.0, (req.temperature - 28.0) / 40.0)
            volume = round(base_volume * temp_factor, 1)
            duration = int(volume * 8)  # rough rule: 1 L/m² ≈ 8 min drip

            notes_map = {
                0: "Apply in early morning to reduce evaporation.",
                1: "Check soil moisture before irrigating.",
                2: "Evening application acceptable if morning is not possible.",
            }
            schedule.append(IrrigationScheduleItem(
                day_offset=day_offset,
                duration_minutes=duration,
                water_volume_liters_per_sqm=volume,
                notes=notes_map[day_offset],
            ))

    return schedule


def _soil_health_notes(req: AdvisoryRequest) -> List[str]:
    notes: List[str] = []
    ph_lo, ph_hi = _crop_ph_range(req.crop_name)

    if req.ph < ph_lo:
        notes.append(
            f"Soil pH {req.ph} is too acidic for {req.crop_name} (optimal: {ph_lo}–{ph_hi}). "
            "Apply agricultural lime to raise pH."
        )
    elif req.ph > ph_hi:
        notes.append(
            f"Soil pH {req.ph} is too alkaline for {req.crop_name} (optimal: {ph_lo}–{ph_hi}). "
            "Apply elemental sulphur to lower pH."
        )
    else:
        notes.append(f"pH {req.ph} is within the optimal range for {req.crop_name} ({ph_lo}–{ph_hi}). ✓")

    lo, hi = _optimal_moisture_range(req.crop_stage.value)
    if req.moisture < lo:
        notes.append(
            f"Soil moisture {req.moisture:.1f}% is below the optimal {lo}–{hi}% for the "
            f"{req.crop_stage.value} stage — irrigation is needed."
        )
    elif req.moisture > hi:
        notes.append(
            f"Soil moisture {req.moisture:.1f}% exceeds the optimal {lo}–{hi}% — "
            "risk of root hypoxia and fungal disease. Consider improving drainage."
        )
    else:
        notes.append(f"Soil moisture {req.moisture:.1f}% is ideal for current growth stage. ✓")

    return notes


def _risk_flags(req: AdvisoryRequest) -> List[str]:
    flags: List[str] = []
    if req.temperature >= HEAT_STRESS_THRESHOLD:
        flags.append(
            f"⚠ Heat stress risk: {req.temperature}°C exceeds {HEAT_STRESS_THRESHOLD}°C threshold. "
            "Consider shade nets and increased irrigation frequency."
        )
    if req.temperature <= COLD_STRESS_THRESHOLD:
        flags.append(
            f"⚠ Cold stress risk: {req.temperature}°C is near or below {COLD_STRESS_THRESHOLD}°C. "
            "Protect sensitive crops with row covers or frost cloths."
        )
    if req.moisture > 80:
        flags.append(
            "⚠ Very high soil moisture — risk of anaerobic root conditions and Phytophthora infection."
        )
    if req.moisture < 20:
        flags.append(
            "⚠ Very low soil moisture — severe drought stress possible. Irrigate immediately."
        )
    if req.rain_prob > 0.8 and req.moisture > 65:
        flags.append(
            "⚠ High rainfall probability combined with already-wet soil — waterlogging risk. "
            "Do NOT irrigate today."
        )
    return flags


def _actionable_tips(
    req: AdvisoryRequest,
    should_irrigate: bool,
    method: IrrigationMethod,
) -> List[str]:
    tips: List[str] = []
    if should_irrigate:
        tips.append(
            f"Irrigate today using {method.value} method. "
            "Schedule for early morning (5–7 AM) to minimise evaporation."
        )
    if req.crop_stage.value in ("flowering", "fruiting"):
        tips.append(
            "During flowering/fruiting, maintain uniform soil moisture to prevent "
            "blossom-drop and fruit cracking."
        )
    if req.soil_type.value == "sandy":
        tips.append(
            "Sandy soils drain quickly — consider more frequent, shorter irrigation sessions "
            "rather than one long event."
        )
    if req.temperature > 30:
        tips.append(
            "High temperatures increase evapotranspiration — monitor soil moisture daily "
            "and adjust schedule dynamically."
        )
    if req.rain_prob > 0.5:
        tips.append(
            f"Rain probability is {req.rain_prob:.0%} — delay irrigation and reassess "
            "after actual rainfall amount is confirmed."
        )
    return tips


# =========================================================================== #
#  Public function — Advisory
# =========================================================================== #


def get_advisory(req: AdvisoryRequest) -> AdvisoryResponse:
    """
    Generate a full irrigation and sustainability advisory for the given field conditions.

    Parameters
    ----------
    req : AdvisoryRequest
        Validated input payload from the API endpoint.

    Returns
    -------
    AdvisoryResponse
        Irrigation schedule, sustainability score, soil notes, risk flags, and tips.
    """
    lo, hi = _optimal_moisture_range(req.crop_stage.value)
    soil_is_dry = req.moisture < lo
    no_rain_expected = req.rain_prob < RAIN_SKIP_THRESHOLD
    should_irrigate = soil_is_dry and no_rain_expected

    method = _best_irrigation_method(req.soil_type.value, req.rain_prob)
    schedule = _build_irrigation_schedule(req, should_irrigate, method)
    score = _compute_sustainability_score(req)

    return AdvisoryResponse(
        crop_name=req.crop_name,
        crop_stage=req.crop_stage.value,
        should_irrigate_today=should_irrigate,
        recommended_method=method,
        irrigation_schedule=schedule,
        sustainability_score=score,
        sustainability_rating=_sustainability_rating(score),
        soil_health_notes=_soil_health_notes(req),
        risk_flags=_risk_flags(req),
        actionable_tips=_actionable_tips(req, should_irrigate, method),
    )


# =========================================================================== #
#  Public function — Weather Risk
# =========================================================================== #


def get_weather_risk(req: WeatherRiskRequest) -> WeatherRiskResponse:
    """
    Return a mock weather risk analysis for the specified location and crop.

    TODO: Replace mock with a real weather API call using settings.WEATHER_API_KEY.
          Recommended provider: OpenWeatherMap One Call API 3.0
          Endpoint: GET {settings.WEATHER_API_BASE_URL}/onecall?lat=...&lon=...
    """
    rng = random.Random(hash(req.location + str(req.days_ahead)))

    daily_forecast: List[Dict[str, Any]] = []
    total_risk = 0.0

    for i in range(req.days_ahead):
        forecast_date = (date.today() + timedelta(days=i)).isoformat()
        temp_max = round(rng.uniform(22, 38), 1)
        temp_min = round(rng.uniform(15, 22), 1)
        humidity = round(rng.uniform(45, 90), 1)
        rain_mm = round(rng.uniform(0, 30), 1)
        wind_kph = round(rng.uniform(5, 40), 1)

        day_risk = 0.0
        if temp_max > HEAT_STRESS_THRESHOLD:
            day_risk += 30.0
        if humidity > 80:
            day_risk += 20.0
        if rain_mm > 20:
            day_risk += 15.0
        if wind_kph > 30:
            day_risk += 10.0

        total_risk += day_risk
        daily_forecast.append({
            "date": forecast_date,
            "temp_max_c": temp_max,
            "temp_min_c": temp_min,
            "humidity_pct": humidity,
            "rain_mm": rain_mm,
            "wind_kph": wind_kph,
            "day_risk_score": round(day_risk, 1),
        })

    avg_risk = round(total_risk / req.days_ahead, 1)

    if avg_risk >= 50:
        risk_level = "Severe"
    elif avg_risk >= 30:
        risk_level = "High"
    elif avg_risk >= 15:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    recommendations = [
        f"Overall {req.days_ahead}-day risk for {req.location} is {risk_level}.",
    ]
    if avg_risk >= 30:
        recommendations.append("Avoid outdoor pesticide spraying — wind and rain reduce efficacy.")
    if any(d["temp_max_c"] > HEAT_STRESS_THRESHOLD for d in daily_forecast):
        recommendations.append("Irrigate early morning on heat-stress days to reduce crop water deficit.")
    if req.crop_name:
        recommendations.append(
            f"Monitor {req.crop_name} closely — apply preventive fungicide if humidity stays above 80%."
        )

    return WeatherRiskResponse(
        location=req.location,
        forecast_days=req.days_ahead,
        overall_risk_level=risk_level,
        risk_index=min(100.0, avg_risk),
        daily_forecast=daily_forecast,
        recommendations=recommendations,
        data_source="mock",
    )
