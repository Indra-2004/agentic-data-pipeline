"""Tests for the policy engine and safety classification."""

from __future__ import annotations

import pytest

from app.agent.policies import ActionClass, PolicyEngine, PolicyError
from app.models import (
    ApprovalStatus,
    FixOperation,
    FixOperationType,
    FixProposal,
    RiskLevel,
)
from app.models.state import Phase


def _proposal(risk: RiskLevel, *ops: FixOperation) -> FixProposal:
    return FixProposal(root_cause="test", operations=list(ops), risk=risk)


def _cast() -> FixOperation:
    return FixOperation(operation=FixOperationType.CAST_TYPE, column="a", to_type="DOUBLE")


