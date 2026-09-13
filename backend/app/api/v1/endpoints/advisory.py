"""
app/api/v1/endpoints/advisory.py
----------------------------------
Bonus Endpoint — Crop Irrigation & Sustainability Advisory

POST /api/v1/advisory/recommend
    • Accepts a JSON payload describing field conditions.
    • Delegates to recommendation.get_advisory() for rule-based analysis.
    • Logs every advisory request to the database (AdvisoryLog).
    • Returns a structured AdvisoryResponse.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.advisory_log import AdvisoryLog
from app.schemas.advisory import AdvisoryRequest, AdvisoryResponse
from app.services.recommendation import get_advisory

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/advisory",
    tags=["💧 Irrigation Advisory"],
)


@router.post(
    "/recommend",
    response_model=AdvisoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get irrigation and sustainability advisory",
    description=(
        "Provide current field conditions — crop stage, soil type, pH, moisture, "
        "temperature, and rain probability — to receive:\n\n"
        "- **Irrigation recommendation** with a 3-day schedule\n"
        "- **Best irrigation method** for your soil type\n"
        "- **Sustainability score** (0–100) with a human-readable rating\n"
        "- **Soil health notes** and **risk flags**\n"
        "- **Actionable tips** ranked by priority\n\n"
        "Every advisory request is logged to the database for retrospective analysis."
    ),
    responses={
        200: {"description": "Advisory generated successfully", "model": AdvisoryResponse},
        422: {"description": "Validation error — check field ranges and enum values"},
        500: {"description": "Internal computation error"},
    },
)
async def get_recommendation(
    req: AdvisoryRequest,
    db: AsyncSession = Depends(get_db),
) -> AdvisoryResponse:
    try:
        result = get_advisory(req)
    except Exception as exc:
        logger.exception("Advisory computation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ADVISORY_COMPUTATION_ERROR",
                "message": "An unexpected error occurred while computing the advisory.",
                "detail": str(exc),
            },
        ) from exc

    # ── Persist to database ──────────────────────────────────────────────────
    try:
        # Summarise the top actionable tip for the log
        recommendation_summary = (
            result.actionable_tips[0] if result.actionable_tips else "No specific tips."
        )
        log_entry = AdvisoryLog(
            crop_type=req.crop_name,
            crop_stage=req.crop_stage.value,
            soil_type=req.soil_type.value,
            ph=req.ph,
            moisture=req.moisture,
            temperature=req.temperature,
            rain_prob=req.rain_prob,
            should_irrigate=result.should_irrigate_today,
            sustainability_score=result.sustainability_score,
            recommendation=recommendation_summary,
        )
        db.add(log_entry)
        await db.commit()
    except Exception as db_exc:
        await db.rollback()
        logger.warning("Failed to log advisory to DB: %s", db_exc)

    logger.info(
        "Advisory: crop=%s stage=%s score=%.1f irrigate=%s",
        result.crop_name,
        result.crop_stage,
        result.sustainability_score,
        result.should_irrigate_today,
    )
    return result
