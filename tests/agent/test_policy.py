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


