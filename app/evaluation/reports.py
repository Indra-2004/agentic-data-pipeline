"""Evaluation reports: markdown + JSON summaries of a scenario run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.evaluation.metrics import EvalMetrics, compute_metrics
from app.evaluation.models import ScenarioResult


def build_report_data(
    results: list[ScenarioResult], metrics: EvalMetrics
) -> dict[str, Any]:
    return {
        "metrics": metrics.to_dict(),
        "scenarios": [r.to_dict() for r in results],
    }


