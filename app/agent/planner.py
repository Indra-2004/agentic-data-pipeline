"""Planner: produce a bounded, ordered plan of steps from a selected hypothesis.

Each :class:`PlanStep` names a tool to call and the phase that gates it. The
planner is deterministic: the same hypothesis yields the same plan. The risk of
the eventual fix determines whether an approval gate is inserted (the policy
engine makes that call, not the planner).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.models import Hypothesis, RiskLevel
from app.models.state import Phase


@dataclass
class PlanStep:
    tool: str
    phase: Phase
    args: dict[str, Any] = field(default_factory=dict)
    description: str = ""


