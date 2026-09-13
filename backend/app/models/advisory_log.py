"""
app/models/advisory_log.py
---------------------------
ORM model for logging irrigation advisory requests.

Every call to POST /api/v1/advisory/recommend writes one row here,
enabling retrospective analysis of field conditions and recommendations.

Columns
-------
id                  Auto-incrementing primary key
crop_type           Name of the crop (e.g., "Tomato", "Wheat")
crop_stage          Growth stage at time of query (e.g., "flowering")
soil_type           Soil classification (e.g., "loamy")
ph                  Soil pH reading supplied by the farmer
moisture            Soil moisture percentage (0–100)
temperature         Ambient temperature in °C
rain_prob           Probability of rain in next 24 h (0.0–1.0)
recommendation      Summary of the recommendation returned
should_irrigate     Whether irrigation was recommended today
sustainability_score Computed sustainability score (0–100)
created_at          UTC timestamp of the advisory request
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AdvisoryLog(Base):
    __tablename__ = "advisory_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)

    crop_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="Name of the crop",
    )
    crop_stage: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        comment="Growth stage (germination / seedling / vegetative / flowering / fruiting / harvest)",
    )
    soil_type: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        comment="Soil classification (clay / sandy / loamy / silty / peaty / chalky / saline)",
    )
    ph: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Soil pH reading (0–14)",
    )
    moisture: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Soil moisture percentage (0–100)",
    )
    temperature: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Ambient temperature in °C",
    )
    rain_prob: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Probability of rain in next 24 h (0.0–1.0)",
    )
    should_irrigate: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        comment="Whether irrigation was recommended today",
    )
    sustainability_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Computed sustainability score (0–100)",
    )
    recommendation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Summarised recommendation text",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="UTC timestamp of the advisory request",
    )

    def __repr__(self) -> str:
        return (
            f"<AdvisoryLog id={self.id} crop={self.crop_type!r} "
            f"stage={self.crop_stage!r} irrigate={self.should_irrigate} at={self.created_at}>"
        )
