"""Statistical anomaly detection (deterministic).

Flags deviations from a historical baseline before any LLM is involved:
  - row count outside 3 sigma (or a minimum absolute drop ratio)
  - null rate spike vs baseline mean
  - mean shift in numeric columns
  - duplicate rate spike
  - category distribution shift

The current observation is measured directly from the DataFrame; the baseline
comes from historical metric snapshots (e.g. ``MetadataStore.get_metric_history``).
"""

from __future__ import annotations

import math
from typing import Any

import polars as pl

from app.models import QualityAnomaly, Severity

SIGMA = 3.0
MIN_ROWS_FOR_BASELINE = 3


def _numeric(history: list[dict[str, Any]], name: str) -> list[float]:
    return [
        float(h[name]) for h in history if name in h and h[name] is not None
    ]


def _mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    n = len(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    return mean, math.sqrt(var)


