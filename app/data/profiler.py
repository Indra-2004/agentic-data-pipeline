"""Dataset profiling: compute deterministic descriptive statistics.

Profiles feed both data quality checks and anomaly detection. Everything here
is computed from the data directly (no LLM involved).
"""

from __future__ import annotations

from typing import Any

import polars as pl


