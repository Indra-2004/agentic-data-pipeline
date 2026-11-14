"""Data quality monitoring.

Runs deterministic checks against a DataFrame and produces a
:class:`QualityReport` plus a list of :class:`QualityAnomaly` objects the agent
uses during diagnosis. All checks are threshold-driven; nothing here is
LLM-decided.
"""

from __future__ import annotations

from typing import Any

import polars as pl

from app.models import (
    QualityAnomaly,
    QualityCheck,
    QualityReport,
    Severity,
)


