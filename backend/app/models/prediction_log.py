"""
app/models/prediction_log.py
-----------------------------
ORM model for logging disease prediction requests.

Every call to POST /api/v1/disease/predict writes one row here,
giving the team an audit trail and a dataset for future model fine-tuning.

Columns
-------
id                  Auto-incrementing primary key
image_name          Original filename of the uploaded image
predicted_disease   Top class label returned by the model
confidence          Prediction confidence score (0.0 – 1.0)
is_healthy          True when the plant was predicted as healthy
severity            "None" / "Low" / "Moderate" / "High"
model_version       Which model version produced this prediction
processing_time_ms  Server-side inference time in milliseconds
created_at          UTC timestamp of the prediction request
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)

    image_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Original filename of the uploaded image",
    )
    predicted_disease: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        comment="Top disease class label returned by the model",
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Prediction confidence score (0.0 – 1.0)",
    )
    is_healthy: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="True when the plant was predicted as healthy",
    )
    severity: Mapped[str | None] = mapped_column(
        String(16),
        nullable=True,
        comment="Severity level: None / Low / Moderate / High",
    )
    model_version: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        comment="Identifier of the model version that produced this prediction",
    )
    processing_time_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Server-side inference time in milliseconds",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="UTC timestamp of the prediction request",
    )

    def __repr__(self) -> str:
        return (
            f"<PredictionLog id={self.id} disease={self.predicted_disease!r} "
            f"confidence={self.confidence:.3f} at={self.created_at}>"
        )
