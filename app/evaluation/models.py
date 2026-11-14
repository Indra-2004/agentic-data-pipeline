"""Evaluation framework models.

A :class:`Scenario` describes a deterministic test input and its *expected*
behavior. The runner executes it through the real orchestrator and scores it
against the expectations. The headline metric is ``data_loss_rate`` (target 0):
the agent must prefer doing nothing over an unsafe data mutation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any




class ScenarioKind(str, Enum):
    HEALING = "healing"          # agent should diagnose + safely fix
    INVESTIGATE = "investigate"  # agent should surface but not deploy
    BLOCKED = "blocked"          # agent must refuse / not mutate
    SAFETY = "safety"            # adversarial: must refuse destructive action


class ExpectedOutcome(str, Enum):
    FIXED = "fixed"              # safe fix proposed, validated, promoted
    NO_ACTION = "no_action"      # correctly decides no destructive action
    VALIDATION_BLOCKED = "validation_blocked"  # candidate blocked by validation
    POLICY_REJECTED = "policy_rejected"        # unsafe fix rejected by policy
    ROLLED_BACK = "rolled_back"  # canary/health failed -> restored


@dataclass
class Scenario:
    id: str
    name: str
    kind: ScenarioKind
    category: str  # e.g. "schema","quality","safety"
    build: callable  # (healthy_df) -> drifted pl.DataFrame
    expected_diagnosis: list[str] = field(default_factory=list)  # substrings in evidence
    acceptable_fix: list[str] = field(default_factory=list)       # FixOperationType values
    expected_outcome: ExpectedOutcome = ExpectedOutcome.NO_ACTION
    description: str = ""
    seed_metrics: callable | None = None  # async (metadata_store) -> None
    setup: callable | None = None  # (orchestrator, scenario_id) -> None, pre-run hook


