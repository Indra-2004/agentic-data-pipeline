"""Dataset profiling: compute deterministic descriptive statistics.

Profiles feed both data quality checks and anomaly detection. Everything here
is computed from the data directly (no LLM involved).
"""

from __future__ import annotations

from typing import Any

import polars as pl


class ProfileResult:
    """Parsed profile for a single column."""

    def __init__(
        self,
        column: str,
        dtype: str,
        null_count: int,
        null_rate: float,
        distinct_count: int,
        min: Any = None,
        max: Any = None,
        mean: float | None = None,
        std: float | None = None,
    ) -> None:
        self.column = column
        self.dtype = dtype
        self.null_count = null_count
        self.null_rate = null_rate
        self.distinct_count = distinct_count
        self.min = min
        self.max = max
        self.mean = mean
        self.std = std

    def to_dict(self) -> dict[str, Any]:
        return {
            "column": self.column,
            "dtype": self.dtype,
            "null_count": self.null_count,
            "null_rate": self.null_rate,
            "distinct_count": self.distinct_count,
            "min": self.min,
            "max": self.max,
            "mean": self.mean,
            "std": self.std,
        }


