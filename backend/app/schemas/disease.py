"""
app/schemas/disease.py
----------------------
Pydantic models for the crop-disease detection endpoint.

Input  → multipart/form-data file upload (handled directly in the router)
Output → DiseasePredictionResponse
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
#  Sub-models
# --------------------------------------------------------------------------- #


class PrecautionItem(BaseModel):
    """A single actionable precaution or treatment recommendation."""

    step: int = Field(..., ge=1, description="Order of the precaution step")
    action: str = Field(..., description="Short imperative action title")
    detail: str = Field(..., description="Expanded guidance for the farmer")

    model_config = {
        "json_schema_extra": {
            "example": {
                "step": 1,
                "action": "Remove infected leaves",
                "detail": (
                    "Carefully cut and bag all visibly infected leaves. "
                    "Do not compost — burn or dispose of them off-site."
                ),
            }
        }
    }


class AlternativePrediction(BaseModel):
    """Runner-up disease prediction returned alongside the top result."""

    class_name: str = Field(..., description="Disease class label")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0–1")


# --------------------------------------------------------------------------- #
#  Primary response model
# --------------------------------------------------------------------------- #


class DiseasePredictionResponse(BaseModel):
    """
    Full prediction response for the POST /api/v1/disease/predict endpoint.
    """

    # Core prediction fields
    class_name: str = Field(
        ...,
        description="Primary disease class predicted by the model",
        examples=["Tomato___Late_blight"],
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score of the top prediction (0.0 – 1.0)",
        examples=[0.923],
    )
    severity: str = Field(
        ...,
        description="Estimated severity level: 'Low', 'Moderate', or 'High'",
        examples=["High"],
    )
    is_healthy: bool = Field(
        ...,
        description="True when the plant is predicted healthy (no disease detected)",
    )

    # Human-readable enrichment
    display_name: str = Field(
        ...,
        description="Friendly, space-separated disease name for UI display",
        examples=["Late Blight"],
    )
    crop_name: str = Field(
        ...,
        description="Host crop name extracted from the class label",
        examples=["Tomato"],
    )
    description: str = Field(
        ...,
        description="Brief description of the disease and its impact",
    )

    # Guidance
    precautions: List[PrecautionItem] = Field(
        default_factory=list,
        description="Ordered list of actionable precautionary / treatment steps",
    )

    # Optional extras
    alternatives: Optional[List[AlternativePrediction]] = Field(
        default=None,
        description="Top-2 runner-up predictions (null when model is in mock mode)",
    )
    model_version: str = Field(
        default="mock-v1.0",
        description="Identifier of the model version that produced this prediction",
    )
    processing_time_ms: Optional[float] = Field(
        default=None,
        description="Server-side inference time in milliseconds",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "class_name": "Tomato___Late_blight",
                "confidence": 0.923,
                "severity": "High",
                "is_healthy": False,
                "display_name": "Late Blight",
                "crop_name": "Tomato",
                "description": (
                    "Late blight is a destructive disease caused by Phytophthora infestans. "
                    "It spreads rapidly in cool, moist conditions and can destroy an entire "
                    "crop within days if left untreated."
                ),
                "precautions": [
                    {
                        "step": 1,
                        "action": "Remove infected tissue",
                        "detail": "Bag and destroy all affected leaves and stems immediately.",
                    },
                    {
                        "step": 2,
                        "action": "Apply fungicide",
                        "detail": "Spray copper-based or mancozeb fungicide at 7-day intervals.",
                    },
                ],
                "alternatives": [
                    {"class_name": "Tomato___Early_blight", "confidence": 0.051},
                    {"class_name": "Tomato___healthy", "confidence": 0.014},
                ],
                "model_version": "mock-v1.0",
                "processing_time_ms": 48.3,
            }
        }
    }


# --------------------------------------------------------------------------- #
#  Error response
# --------------------------------------------------------------------------- #


class PredictionError(BaseModel):
    """Returned when the uploaded file cannot be processed."""

    error: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error description")
    detail: Optional[str] = Field(default=None, description="Optional stack trace / extra info")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "INVALID_IMAGE",
                "message": "The uploaded file could not be decoded as an image.",
                "detail": "Unsupported format: application/pdf",
            }
        }
    }
