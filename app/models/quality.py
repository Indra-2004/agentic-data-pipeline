"""Data quality metrics, checks, and quality anomaly models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.models.schema import Severity


class QualityCheck(BaseModel):
    """A single quality check definition + observed result."""

    name: str
    column: str | None = None
    metric: str  # e.g. "null_rate", "duplicate_rate", "row_count", "range"
    threshold: float | None = None
    observed: float | None = None
    status: str = "pending"  # pass | fail | skip
    message: str | None = None


