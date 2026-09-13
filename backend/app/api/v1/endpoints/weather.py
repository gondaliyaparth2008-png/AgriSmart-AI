"""
app/api/v1/endpoints/weather.py
---------------------------------
Bonus Endpoint — Live Weather Intelligence & Risk Analysis

POST /api/v1/weather/risk
    • Accepts a location (city name or "lat,lon") + optional crop name.
    • Fetches live data from OpenWeatherMap (falls back to mock if key absent).
    • Returns a multi-day forecast with per-day risk scores and actionable alerts.

GET /api/v1/weather/current
    • Returns current conditions for a given location with a risk alert.

All fetching is delegated to app/services/weather_service.py.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.advisory import WeatherRiskRequest, WeatherRiskResponse
from app.services.weather_service import (
    build_risk_alert,
    get_current_weather,
    get_forecast,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/weather",
    tags=["⛅ Weather Intelligence"],
)


# --------------------------------------------------------------------------- #
#  POST /risk  — Multi-day forecast + risk analysis
# --------------------------------------------------------------------------- #


@router.post(
    "/risk",
    response_model=WeatherRiskResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyse weather risk for a location and crop",
    description=(
        "Submit a location and optional crop name to receive a multi-day weather risk report:\n\n"
        "- **Daily forecast** with temperature, humidity, rainfall, and wind\n"
        "- **Per-day risk score** based on agronomic thresholds\n"
        "- **Aggregate risk level**: Low / Moderate / High / Severe\n"
        "- **Crop-specific recommendations** for the forecast window\n\n"
        "**Data source:** Live OpenWeatherMap (set `WEATHER_API_KEY` in `.env`). "
        "Returns mock data when key is absent."
    ),
    responses={
        200: {"description": "Weather risk report generated", "model": WeatherRiskResponse},
        422: {"description": "Validation error"},
        500: {"description": "Weather service error"},
    },
)
async def weather_risk(req: WeatherRiskRequest) -> WeatherRiskResponse:
    try:
        daily_forecast, data_source = await get_forecast(req.location, req.days_ahead)
    except Exception as exc:
        logger.exception("Weather risk fetch failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "WEATHER_SERVICE_ERROR",
                "message": "Failed to retrieve or analyse weather data.",
                "detail": str(exc),
            },
        ) from exc

    # Aggregate risk
    total_risk = sum(d.get("day_risk_score", 0) for d in daily_forecast)
    avg_risk = round(total_risk / max(len(daily_forecast), 1), 1)

    if avg_risk >= 50:
        risk_level = "Severe"
    elif avg_risk >= 30:
        risk_level = "High"
    elif avg_risk >= 15:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    # Build recommendations
    recommendations = [
        f"Overall {req.days_ahead}-day risk for {req.location} is classified as {risk_level}."
    ]
    if any(d.get("rain_mm", 0) > 5 for d in daily_forecast):
        recommendations.append(
            "Rain forecast: delay irrigation on rainy days and avoid pesticide spraying."
        )
    if any(d.get("humidity_pct", 0) > 80 for d in daily_forecast):
        recommendations.append(
            "High humidity expected: apply precautionary anti-fungal spray to reduce disease risk."
        )
    if any(d.get("temp_max_c", 0) > 37 for d in daily_forecast):
        recommendations.append(
            "Heat stress risk: irrigate early morning and consider shade nets for sensitive crops."
        )
    if req.crop_name:
        recommendations.append(
            f"Monitor {req.crop_name} closely and scout twice weekly during this forecast window."
        )

    logger.info(
        "Weather risk: location=%s days=%d risk=%s (%.1f) source=%s",
        req.location, req.days_ahead, risk_level, avg_risk, data_source,
    )

    return WeatherRiskResponse(
        location=req.location,
        forecast_days=req.days_ahead,
        overall_risk_level=risk_level,
        risk_index=min(100.0, avg_risk),
        daily_forecast=daily_forecast,
        recommendations=recommendations,
        data_source=data_source,
    )


# --------------------------------------------------------------------------- #
#  GET /current  — Live current conditions
# --------------------------------------------------------------------------- #


@router.get(
    "/current",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get current weather conditions",
    description=(
        "Returns current weather for a given city or coordinates, including:\n\n"
        "- Temperature, humidity, wind speed, and condition\n"
        "- Rainfall in the last hour\n"
        "- An **actionable risk alert** tailored to the current conditions\n\n"
        "**Data source:** Live OpenWeatherMap (set `WEATHER_API_KEY` in `.env`). "
        "Returns deterministic mock data when key is absent."
    ),
)
async def current_weather(
    location: str = Query(
        ...,
        min_length=2,
        description=(
            "City name (e.g. 'Hyderabad') or 'lat,lon' coordinates "
            "(e.g. '17.38,78.48')"
        ),
        examples=["Hyderabad"],
    ),
    crop: str = Query(
        default="",
        description="Optional crop name for a crop-specific risk alert",
        examples=["Tomato"],
    ),
) -> Dict[str, Any]:
    try:
        data = await get_current_weather(location)
    except Exception as exc:
        logger.exception("Current weather fetch failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "WEATHER_FETCH_ERROR",
                "message": "Failed to retrieve current weather.",
                "detail": str(exc),
            },
        ) from exc

    # Attach a risk alert
    risk_alert = build_risk_alert(
        temp_c=data.get("temperature_c", 25),
        humidity_pct=data.get("humidity_pct", 60),
        condition=data.get("condition", "Clear"),
        rain_mm=data.get("rain_mm_1h", 0.0),
        wind_kph=data.get("wind_kph", 10.0),
        crop_name=crop or None,
    )
    data["risk_alert"] = risk_alert

    logger.info(
        "Current weather: location=%s temp=%.1f°C source=%s",
        location, data.get("temperature_c", 0), data.get("data_source", "?"),
    )
    return data
