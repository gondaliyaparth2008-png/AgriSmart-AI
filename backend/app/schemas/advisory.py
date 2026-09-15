"""
app/schemas/advisory.py
-----------------------
Pydantic models for:
  • POST /api/v1/advisory/recommend  — irrigation & sustainability advisory
  • POST /api/v1/weather/risk        — weather risk analysis
  • POST /api/v1/assistant/query     — GenAI farmer assistant
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# =========================================================================== #
#  Shared enumerations
# =========================================================================== #


class CropStage(str, Enum):
    GERMINATION = "germination"
    SEEDLING = "seedling"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    HARVEST = "harvest"


class SoilType(str, Enum):
    CLAY = "clay"
    SANDY = "sandy"
    LOAMY = "loamy"
    SILTY = "silty"
    PEATY = "peaty"
    CHALKY = "chalky"
    SALINE = "saline"


class IrrigationMethod(str, Enum):
    DRIP = "drip"
    SPRINKLER = "sprinkler"
    FLOOD = "flood"
    FURROW = "furrow"
    NONE = "none"


# =========================================================================== #
#  Advisory  — Request / Response
# =========================================================================== #


class AdvisoryRequest(BaseModel):
    """Input payload for the crop irrigation & sustainability advisory endpoint."""

    crop_name: str = Field(
        ...,
        min_length=2,
        max_length=64,
        description="Name of the crop (e.g. 'Tomato', 'Wheat', 'Paddy')",
        examples=["Tomato"],
    )
    crop_stage: CropStage = Field(
        ...,
        description="Current growth stage of the crop",
        examples=[CropStage.FLOWERING],
    )
    soil_type: SoilType = Field(
        ...,
        description="Dominant soil classification of the field",
        examples=[SoilType.LOAMY],
    )
    ph: float = Field(
        ...,
        ge=0.0,
        le=14.0,
        description="Soil pH reading (0–14)",
        examples=[6.5],
    )
    moisture: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Current soil moisture percentage (0–100 %)",
        examples=[42.0],
    )
    temperature: float = Field(
        ...,
        ge=-20.0,
        le=60.0,
        description="Ambient / field temperature in °C",
        examples=[28.5],
    )
    rain_prob: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Probability of rain in the next 24 h (0.0 – 1.0)",
        examples=[0.25],
    )
    current_irrigation_method: Optional[IrrigationMethod] = Field(
        default=IrrigationMethod.NONE,
        description="Irrigation method currently in use (optional)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "crop_name": "Tomato",
                "crop_stage": "flowering",
                "soil_type": "loamy",
                "ph": 6.5,
                "moisture": 42.0,
                "temperature": 28.5,
                "rain_prob": 0.25,
                "current_irrigation_method": "drip",
            }
        }
    }


class IrrigationScheduleItem(BaseModel):
    """A single entry in the recommended irrigation schedule."""

    day_offset: int = Field(..., ge=0, description="Days from today (0 = today)")
    duration_minutes: int = Field(..., ge=0, description="Recommended irrigation duration")
    water_volume_liters_per_sqm: float = Field(
        ..., ge=0.0, description="Estimated water needed per square metre"
    )
    notes: str = Field(default="", description="Context-specific note for this day")


class AdvisoryResponse(BaseModel):
    """Full advisory response with irrigation plan, sustainability score, and tips."""

    crop_name: str = Field(..., description="Echo of the queried crop")
    crop_stage: str = Field(..., description="Echo of the queried growth stage")

    # Irrigation recommendation
    should_irrigate_today: bool = Field(
        ..., description="True if irrigation is recommended today"
    )
    recommended_method: IrrigationMethod = Field(
        ..., description="Best-fit irrigation method for the given conditions"
    )
    irrigation_schedule: List[IrrigationScheduleItem] = Field(
        default_factory=list,
        description="3-day ahead irrigation schedule",
    )

    # Sustainability
    sustainability_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description=(
            "Composite sustainability score (0–100) computed from water efficiency, "
            "soil health indicators, and weather alignment."
        ),
    )
    sustainability_rating: str = Field(
        ...,
        description="Human label: 'Excellent', 'Good', 'Fair', or 'Poor'",
    )

    # Agronomic insights
    soil_health_notes: List[str] = Field(
        default_factory=list,
        description="Observations about soil pH, moisture, and type compatibility",
    )
    risk_flags: List[str] = Field(
        default_factory=list,
        description="Potential risks detected (e.g. over-irrigation, frost, drought stress)",
    )
    actionable_tips: List[str] = Field(
        default_factory=list,
        description="Ranked list of immediate actions the farmer should take",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "crop_name": "Tomato",
                "crop_stage": "flowering",
                "should_irrigate_today": True,
                "recommended_method": "drip",
                "irrigation_schedule": [
                    {
                        "day_offset": 0,
                        "duration_minutes": 30,
                        "water_volume_liters_per_sqm": 3.5,
                        "notes": "Soil moisture below optimal for flowering stage.",
                    }
                ],
                "sustainability_score": 74.5,
                "sustainability_rating": "Good",
                "soil_health_notes": [
                    "pH 6.5 is ideal for Tomato.",
                    "Loamy soil retains moisture well — avoid over-irrigation.",
                ],
                "risk_flags": ["Moderate heat stress risk at 28.5 °C"],
                "actionable_tips": [
                    "Irrigate early morning to minimise evaporation losses.",
                    "Monitor for blossom-drop if temperature exceeds 32 °C.",
                ],
            }
        }
    }


# =========================================================================== #
#  Weather  — Request / Response
# =========================================================================== #


class WeatherRiskRequest(BaseModel):
    """Request payload for the weather risk analysis endpoint."""

    location: str = Field(
        ...,
        min_length=2,
        description="City name or 'lat,lon' coordinate string",
        examples=["Hyderabad"],
    )
    crop_name: Optional[str] = Field(
        default=None,
        description="Crop for crop-specific weather risk context (optional)",
        examples=["Tomato"],
    )
    days_ahead: int = Field(
        default=3,
        ge=1,
        le=7,
        description="Number of forecast days to analyse (1–7)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {"location": "Hyderabad", "crop_name": "Tomato", "days_ahead": 3}
        }
    }


class WeatherRiskResponse(BaseModel):
    """Weather risk analysis response with per-day forecast and aggregate risk index."""

    location: str
    forecast_days: int
    overall_risk_level: str = Field(
        ..., description="Aggregate risk: 'Low', 'Moderate', 'High', or 'Severe'"
    )
    risk_index: float = Field(..., ge=0.0, le=100.0, description="Numeric risk score 0–100")
    daily_forecast: List[Dict[str, Any]] = Field(
        default_factory=list, description="Per-day weather + risk summary"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Weather-driven crop management recommendations"
    )
    data_source: str = Field(default="mock", description="Weather data provider identifier")


# =========================================================================== #
#  Assistant  — Request / Response
# =========================================================================== #


class SupportedLanguage(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    TELUGU = "te"
    TAMIL = "ta"
    KANNADA = "kn"
    MARATHI = "mr"
    BENGALI = "bn"
    PUNJABI = "pa"
    GUJARATI = "gu"


class AssistantRequest(BaseModel):
    """Input payload for the GenAI farmer assistant endpoint."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=1024,
        description="Farmer's question or problem description",
        examples=["My tomato leaves are turning yellow. What should I do?"],
    )
    language: SupportedLanguage = Field(
        default=SupportedLanguage.ENGLISH,
        description="Preferred response language (ISO 639-1 code)",
    )
    context: Optional[str] = Field(
        default=None,
        max_length=2048,
        description=(
            "Optional surrounding context — e.g. previous conversation turns, "
            "detected disease class, or field conditions — to ground the response."
        ),
        examples=["Disease detected: Tomato Late Blight. Confidence: 0.92."],
    )

    @field_validator("query")
    @classmethod
    def query_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("query must not be blank or whitespace only")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "My tomato leaves are turning yellow and have dark spots.",
                "language": "en",
                "context": "Disease detected: Tomato Late Blight. Confidence: 0.92.",
            }
        }
    }


class AssistantSource(BaseModel):
    """A cited knowledge source for the assistant's answer."""

    title: str
    relevance: str = Field(..., description="Why this source is relevant to the query")


class AssistantResponse(BaseModel):
    """Structured response from the GenAI farmer assistant."""

    answer: str = Field(..., description="Farmer-friendly, actionable answer in the requested language")
    language: str = Field(..., description="ISO language code of the response")
    follow_up_questions: List[str] = Field(
        default_factory=list,
        description="Suggested follow-up questions to help the farmer dig deeper",
    )
    sources: List[AssistantSource] = Field(
        default_factory=list,
        description="Knowledge sources cited in the answer",
    )
    confidence: str = Field(
        default="high",
        description="Assistant's self-assessed confidence: 'high', 'medium', or 'low'",
    )
    powered_by: str = Field(
        default="AgriSmart AI Mock Engine",
        description="Backend engine that generated this response",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "answer": (
                    "The yellow leaves with dark spots strongly suggest Late Blight infection. "
                    "Act immediately: (1) Remove and destroy all infected leaves. "
                    "(2) Apply a copper-based fungicide every 7 days. "
                    "(3) Avoid overhead irrigation — switch to drip if possible. "
                    "(4) Improve air circulation by pruning dense foliage."
                ),
                "language": "en",
                "follow_up_questions": [
                    "How long has the yellowing been visible?",
                    "Is the discolouration spreading to stems as well?",
                    "What fungicides are available at your local agri-shop?",
                ],
                "sources": [
                    {
                        "title": "ICAR Late Blight Management Guide",
                        "relevance": "Covers fungicide schedules for Phytophthora infestans",
                    }
                ],
                "confidence": "high",
                "powered_by": "AgriSmart AI Mock Engine",
            }
        }
    }
