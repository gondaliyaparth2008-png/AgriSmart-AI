"""
app/services/weather_service.py
---------------------------------
Live weather data service using the OpenWeatherMap REST API.

Public functions
----------------
    get_current_weather(location: str) -> dict
    get_forecast(location: str, days: int) -> dict
    build_risk_alert(weather_data: dict, crop_name: str | None) -> str

Fallback behaviour
------------------
When WEATHER_API_KEY is not set in .env, both functions return a
deterministic mock response and log a warning — the server never crashes.

API reference
-------------
Current weather:  GET {BASE_URL}/weather?q={city}&appid={key}&units=metric
5-day forecast:   GET {BASE_URL}/forecast?q={city}&cnt={cnt}&appid={key}&units=metric
By coordinates:   ?lat={lat}&lon={lon}&appid={key}&units=metric
"""

from __future__ import annotations

import logging
import random
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# OpenWeatherMap condition code → agronomic label
_OWM_CONDITION_MAP: Dict[str, str] = {
    "Thunderstorm": "Severe storm",
    "Drizzle":      "Light rain",
    "Rain":         "Rain",
    "Snow":         "Snow",
    "Mist":         "Mist",
    "Smoke":        "Haze",
    "Haze":         "Haze",
    "Dust":         "Dusty",
    "Fog":          "Fog",
    "Tornado":      "Tornado",
    "Clear":        "Clear sky",
    "Clouds":       "Cloudy",
}

# ────────────────────────────────────────────────────────────────────────────
#  Risk alert logic
# ────────────────────────────────────────────────────────────────────────────

def build_risk_alert(
    temp_c: float,
    humidity_pct: float,
    condition: str,
    rain_mm: float = 0.0,
    wind_kph: float = 0.0,
    crop_name: Optional[str] = None,
) -> str:
    """
    Generate a single actionable risk alert sentence based on weather parameters.

    Examples
    --------
    "Rain expected: Delay irrigation and avoid pesticide spraying."
    "High humidity (85%): Spray precautionary anti-fungal to reduce disease risk."
    "Heat stress risk (38°C): Irrigate early morning and consider shade nets."
    """
    alerts: List[str] = []

    if condition in ("Rain", "Drizzle", "Thunderstorm") or rain_mm > 5:
        alerts.append("Rain expected — delay irrigation and avoid pesticide spraying.")

    if humidity_pct >= 85:
        alerts.append(
            f"High humidity ({humidity_pct:.0f}%) — spray precautionary anti-fungal "
            "to reduce late blight and fungal disease risk."
        )

    if temp_c >= 37:
        alerts.append(
            f"Heat stress risk ({temp_c:.1f}°C) — irrigate early morning and "
            "consider shade nets for sensitive crops."
        )
    elif temp_c <= 5:
        alerts.append(
            f"Cold stress risk ({temp_c:.1f}°C) — protect crops with row covers "
            "or frost cloth tonight."
        )

    if wind_kph >= 40:
        alerts.append(
            f"High wind speed ({wind_kph:.0f} km/h) — delay chemical spray "
            "to prevent drift and uneven coverage."
        )

    if not alerts:
        base = "Weather conditions are favourable for field operations."
        if crop_name:
            base += f" Monitor {crop_name} for early signs of pest pressure."
        return base

    crop_prefix = f"[{crop_name}] " if crop_name else ""
    return crop_prefix + " ".join(alerts)


# ────────────────────────────────────────────────────────────────────────────
#  Mock helpers
# ────────────────────────────────────────────────────────────────────────────

def _mock_current(location: str) -> Dict[str, Any]:
    """Return a deterministic mock current-weather payload."""
    rng = random.Random(hash(location))
    temp = round(rng.uniform(20, 38), 1)
    humidity = round(rng.uniform(45, 90), 1)
    wind_kph = round(rng.uniform(5, 45), 1)
    condition = rng.choice(["Clear", "Clouds", "Rain", "Drizzle"])
    rain_mm = round(rng.uniform(0, 15), 1) if condition in ("Rain", "Drizzle") else 0.0

    return {
        "location": location,
        "temperature_c": temp,
        "feels_like_c": round(temp + rng.uniform(-3, 5), 1),
        "humidity_pct": humidity,
        "wind_kph": wind_kph,
        "condition": _OWM_CONDITION_MAP.get(condition, condition),
        "rain_mm_1h": rain_mm,
        "uv_index": round(rng.uniform(1, 11), 1),
        "rain_probability": round(rng.uniform(0, 1), 2),
        "data_source": "mock",
        "note": "Set WEATHER_API_KEY in .env to enable live data.",
    }


def _mock_forecast(location: str, days: int) -> List[Dict[str, Any]]:
    """Return deterministic mock daily forecast entries."""
    from datetime import date, timedelta

    rng = random.Random(hash(location + str(days)))
    forecast = []
    for i in range(days):
        day = (date.today() + timedelta(days=i)).isoformat()
        temp_max = round(rng.uniform(24, 40), 1)
        temp_min = round(rng.uniform(15, 24), 1)
        humidity = round(rng.uniform(40, 90), 1)
        rain_mm = round(rng.uniform(0, 30), 1)
        wind_kph = round(rng.uniform(5, 45), 1)
        condition = rng.choice(["Clear", "Clouds", "Rain"])

        risk_score = 0.0
        if temp_max > 37:
            risk_score += 30
        if humidity > 80:
            risk_score += 20
        if rain_mm > 20:
            risk_score += 15
        if wind_kph > 35:
            risk_score += 10

        forecast.append({
            "date": day,
            "temp_max_c": temp_max,
            "temp_min_c": temp_min,
            "humidity_pct": humidity,
            "rain_mm": rain_mm,
            "wind_kph": wind_kph,
            "condition": _OWM_CONDITION_MAP.get(condition, condition),
            "day_risk_score": round(risk_score, 1),
        })
    return forecast


# ────────────────────────────────────────────────────────────────────────────
#  Live API helpers
# ────────────────────────────────────────────────────────────────────────────

def _parse_location(location: str) -> Dict[str, Any]:
    """
    Parse a location string into OWM query parameters.

    Accepts:
        "Hyderabad"     → {"q": "Hyderabad"}
        "17.38,78.48"   → {"lat": "17.38", "lon": "78.48"}
    """
    parts = location.split(",")
    if len(parts) == 2:
        try:
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            return {"lat": str(lat), "lon": str(lon)}
        except ValueError:
            pass
    return {"q": location.strip()}


async def _owm_get(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform a GET request to the OpenWeatherMap API.

    Raises
    ------
    httpx.HTTPStatusError
        On non-2xx responses.
    httpx.RequestError
        On network failures.
    """
    base = str(settings.WEATHER_API_BASE_URL).rstrip("/")
    url = f"{base}/{endpoint}"
    params["appid"] = settings.WEATHER_API_KEY
    params["units"] = "metric"

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


async def _live_current(location: str) -> Dict[str, Any]:
    """Fetch current weather from OWM /weather endpoint."""
    params = _parse_location(location)
    data = await _owm_get("weather", params)

    rain_mm = data.get("rain", {}).get("1h", 0.0)
    wind_kph = round(data.get("wind", {}).get("speed", 0) * 3.6, 1)  # m/s → km/h
    main = data.get("main", {})
    weather = data.get("weather", [{}])[0]
    condition_raw = weather.get("main", "Clear")

    return {
        "location": data.get("name", location),
        "temperature_c": round(main.get("temp", 0), 1),
        "feels_like_c": round(main.get("feels_like", 0), 1),
        "humidity_pct": round(main.get("humidity", 0), 1),
        "wind_kph": wind_kph,
        "condition": _OWM_CONDITION_MAP.get(condition_raw, condition_raw),
        "rain_mm_1h": rain_mm,
        "uv_index": None,           # UV index requires a separate OWM One Call API call
        "rain_probability": None,   # Not available in /weather endpoint
        "data_source": "openweathermap",
        "raw_condition_code": weather.get("id"),
    }


async def _live_forecast(location: str, days: int) -> List[Dict[str, Any]]:
    """
    Fetch a multi-day forecast from OWM /forecast (5-day / 3-hour intervals).

    The /forecast endpoint returns data in 3-hour blocks. We aggregate to daily.
    `days` is capped at 5 (OWM free tier limit).
    """
    from datetime import date, timedelta
    from collections import defaultdict

    cnt = min(days * 8, 40)  # 8 x 3h blocks = 1 day; max 40 = 5 days
    params = _parse_location(location)
    params["cnt"] = str(cnt)
    data = await _owm_get("forecast", params)

    daily: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "temps": [], "humidities": [], "rain_mms": [], "wind_kphs": [], "conditions": []
    })

    for item in data.get("list", []):
        # OWM returns UTC timestamps
        dt_txt: str = item.get("dt_txt", "")
        day_key = dt_txt[:10]  # "YYYY-MM-DD"
        main = item.get("main", {})
        daily[day_key]["temps"].append(main.get("temp", 0))
        daily[day_key]["humidities"].append(main.get("humidity", 0))
        daily[day_key]["rain_mms"].append(item.get("rain", {}).get("3h", 0.0))
        daily[day_key]["wind_kphs"].append(item.get("wind", {}).get("speed", 0) * 3.6)
        cond_raw = item.get("weather", [{}])[0].get("main", "Clear")
        daily[day_key]["conditions"].append(cond_raw)

    result = []
    today = date.today()
    for i in range(days):
        day_key = (today + timedelta(days=i)).isoformat()
        d = daily.get(day_key)
        if not d or not d["temps"]:
            continue  # no data for this day in OWM response

        temp_max = round(max(d["temps"]), 1)
        temp_min = round(min(d["temps"]), 1)
        humidity = round(sum(d["humidities"]) / len(d["humidities"]), 1)
        rain_mm = round(sum(d["rain_mms"]), 1)
        wind_kph = round(max(d["wind_kphs"]), 1)
        condition_raw = max(set(d["conditions"]), key=d["conditions"].count)  # mode

        risk_score = 0.0
        if temp_max > 37:
            risk_score += 30
        if humidity > 80:
            risk_score += 20
        if rain_mm > 20:
            risk_score += 15
        if wind_kph > 35:
            risk_score += 10

        result.append({
            "date": day_key,
            "temp_max_c": temp_max,
            "temp_min_c": temp_min,
            "humidity_pct": humidity,
            "rain_mm": rain_mm,
            "wind_kph": wind_kph,
            "condition": _OWM_CONDITION_MAP.get(condition_raw, condition_raw),
            "day_risk_score": round(risk_score, 1),
        })

    return result


# ────────────────────────────────────────────────────────────────────────────
#  Public async functions
# ────────────────────────────────────────────────────────────────────────────

async def get_current_weather(location: str) -> Dict[str, Any]:
    """
    Return current weather for a location (city name or "lat,lon").

    Falls back to mock data if WEATHER_API_KEY is not configured or
    if the API request fails.
    """
    if not settings.WEATHER_API_KEY:
        logger.warning(
            "⚠  WEATHER_API_KEY not set — returning mock weather for '%s'.", location
        )
        return _mock_current(location)

    try:
        data = await _live_current(location)
        logger.info("✅ Live weather fetched for '%s' from OWM.", location)
        return data
    except httpx.HTTPStatusError as exc:
        logger.error(
            "OWM API error %d for '%s': %s — falling back to mock.",
            exc.response.status_code, location, exc,
        )
        return {**_mock_current(location), "data_source": "mock_fallback", "api_error": str(exc)}
    except httpx.RequestError as exc:
        logger.error(
            "Network error fetching weather for '%s': %s — falling back to mock.", location, exc
        )
        return {**_mock_current(location), "data_source": "mock_fallback", "api_error": str(exc)}


async def get_forecast(location: str, days: int = 3) -> Tuple[List[Dict[str, Any]], str]:
    """
    Return a multi-day weather forecast for a location.

    Returns
    -------
    (daily_forecast_list, data_source_string)
    """
    days = max(1, min(days, 5))  # OWM free tier: max 5 days

    if not settings.WEATHER_API_KEY:
        logger.warning(
            "⚠  WEATHER_API_KEY not set — returning mock forecast for '%s'.", location
        )
        return _mock_forecast(location, days), "mock"

    try:
        forecast = await _live_forecast(location, days)
        return forecast, "openweathermap"
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        logger.error(
            "OWM forecast error for '%s': %s — falling back to mock.", location, exc
        )
        return _mock_forecast(location, days), "mock_fallback"
