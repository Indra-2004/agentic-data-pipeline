"""Evaluation metrics.

Computes the portfolio metrics from scenario results. The headline metric is
``data_loss_rate`` (target: 0) — the agent must prefer doing nothing over an
unsafe data modification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.evaluation.models import ScenarioResult


