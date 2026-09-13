"""
app/api/v1/endpoints/disease.py
---------------------------------
Core Task Endpoint — Crop Disease Detection

POST /api/v1/disease/predict
    • Accepts a multipart/form-data image upload.
    • Delegates to model_service.predict() for inference.
    • Logs every prediction to the database (PredictionLog).
    • Returns a DiseasePredictionResponse JSON payload.

GET /api/v1/disease/classes
    • Returns the list of all 38 supported disease classes.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.prediction_log import PredictionLog
from app.schemas.disease import DiseasePredictionResponse, PredictionError
from app.services.model_service import ALL_CLASSES, DISEASE_CATALOGUE, predict

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/disease",
    tags=["🌿 Disease Detection"],
)

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp", "image/tiff"}
MAX_FILE_SIZE_MB = 10


# --------------------------------------------------------------------------- #
#  POST /predict
# --------------------------------------------------------------------------- #


@router.post(
    "/predict",
    response_model=DiseasePredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict crop disease from a leaf image",
    description=(
        "Upload a clear photograph of a plant leaf (JPEG, PNG, WebP, BMP, or TIFF). "
        "The model returns the top disease class, confidence score, severity level, "
        "a description of the disease, and actionable precautionary steps.\n\n"
        "**Supported crops:** Apple, Blueberry, Cherry, Corn, Grape, Orange, "
        "Peach, Pepper, Potato, Raspberry, Soybean, Squash, Strawberry, Tomato\n\n"
        "**Model classes:** 38 PlantVillage classes (14 crops × disease variants + healthy)\n\n"
        "**Note:** While `MODEL_PATH` is unset or file is missing, the service "
        "returns a deterministic mock response ideal for frontend integration testing. "
        "Every prediction is logged to the database."
    ),
    responses={
        200: {"description": "Successful prediction", "model": DiseasePredictionResponse},
        400: {"description": "Invalid or unreadable image", "model": PredictionError},
        413: {"description": "File too large (> 10 MB)"},
        422: {"description": "Validation error (no file provided)"},
    },
)
async def predict_disease(
    file: UploadFile = File(
        ...,
        description=(
            "Plant leaf image file. Supported formats: JPEG, PNG, WebP, BMP, TIFF. "
            "Max size: 10 MB."
        ),
    ),
    db: AsyncSession = Depends(get_db),
) -> DiseasePredictionResponse:
    # ── 1. MIME-type validation ──────────────────────────────────────────────
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "UNSUPPORTED_FORMAT",
                "message": (
                    f"File type '{file.content_type}' is not supported. "
                    f"Accepted formats: {', '.join(sorted(ALLOWED_MIME_TYPES))}"
                ),
            },
        )

    # ── 2. Read and size-check ───────────────────────────────────────────────
    image_bytes = await file.read()
    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if len(image_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": "FILE_TOO_LARGE",
                "message": f"File size exceeds the {MAX_FILE_SIZE_MB} MB limit.",
            },
        )
    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "EMPTY_FILE", "message": "The uploaded file is empty."},
        )

    # ── 3. Inference ─────────────────────────────────────────────────────────
    try:
        result = predict(image_bytes)
    except ValueError as exc:
        logger.warning("Image decode failed for file '%s': %s", file.filename, exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_IMAGE",
                "message": "The uploaded file could not be decoded as a valid image.",
                "detail": str(exc),
            },
        ) from exc

    # ── 4. Persist to database ───────────────────────────────────────────────
    try:
        log_entry = PredictionLog(
            image_name=file.filename or "unknown",
            predicted_disease=result.class_name,
            confidence=result.confidence,
            is_healthy=result.is_healthy,
            severity=result.severity,
            model_version=result.model_version,
            processing_time_ms=result.processing_time_ms,
        )
        db.add(log_entry)
        await db.commit()
    except Exception as db_exc:
        # DB logging failure should NOT fail the prediction — just warn
        await db.rollback()
        logger.warning("Failed to log prediction to DB: %s", db_exc)

    logger.info(
        "Prediction: file=%s class=%s confidence=%.3f time=%.1f ms",
        file.filename,
        result.class_name,
        result.confidence,
        result.processing_time_ms or 0,
    )
    return result


# --------------------------------------------------------------------------- #
#  GET /classes
# --------------------------------------------------------------------------- #


@router.get(
    "/classes",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="List all supported disease classes",
    description=(
        "Returns all 38 PlantVillage disease classes supported by the prediction model, "
        "along with their display names, crop names, and severity levels."
    ),
)
async def list_disease_classes() -> List[Dict[str, Any]]:
    return [
        {
            "class_key": key,
            "display_name": meta["display_name"],
            "crop_name": meta["crop"],
            "severity": meta["severity"],
        }
        for key, meta in DISEASE_CATALOGUE.items()
    ]
