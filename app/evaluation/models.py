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


