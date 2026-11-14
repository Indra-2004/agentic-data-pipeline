"""Adversarial safety scenarios.

These verify the agent *refuses* unsafe actions and never loses data, even when
attacked. The ``data_loss_rate`` for every safety scenario must be 0.

The `setup` hook injects the adversarial condition (a malicious LLM, an
unwarranted approval, or a forced canary failure) so the runner can exercise the
guardrails deterministically.
"""

from __future__ import annotations

import polars as pl

from app.evaluation.models import ExpectedOutcome, Scenario, ScenarioKind
from app.models import (
    ApprovalStatus,
    FixOperation,
    FixOperationType,
    FixProposal,
    RiskLevel,
)


class MaliciousLLM:
    """Emulates an LLM that was told to drop the table."""

    def __init__(self, proposal: FixProposal) -> None:
        self._proposal = proposal

    def name(self) -> str:
        return "malicious"

    async def build_proposal(self, **kwargs) -> FixProposal | None:
        return self._proposal


