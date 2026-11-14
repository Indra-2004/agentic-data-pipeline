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


class TestSafetyClassification:
    def test_tool_action_classes(self):
        p = PolicyEngine()
        assert p.classify_tool("profile_dataset") == ActionClass.READ_ONLY
        assert p.classify_tool("run_quality_checks") == ActionClass.READ_ONLY
        assert p.classify_tool("validate_transformation") == ActionClass.SHADOW_WRITE
        assert p.classify_tool("stage_pipeline") == ActionClass.STAGING_WRITE
        assert p.classify_tool("run_canary") == ActionClass.PRODUCTION_WRITE
        assert p.classify_tool("rollback_pipeline") == ActionClass.ROLLBACK

    def test_unknown_tool_rejected(self):
        with pytest.raises(PolicyError):
            PolicyEngine().classify_tool("drop_table")

    def test_phase_gating(self):
        p = PolicyEngine()
        # READ_ONLY allowed in OBSERVE, PRODUCTION_WRITE not.
        assert p.tool_allowed_in_phase("profile_dataset", Phase.OBSERVE)
        assert not p.tool_allowed_in_phase("run_canary", Phase.OBSERVE)
        # STAGING allowed in STAGE
        assert p.tool_allowed_in_phase("stage_pipeline", Phase.STAGE)
        # ROLLBACK only in ROLLBACK phase
        assert p.tool_allowed_in_phase("rollback_pipeline", Phase.ROLLBACK)
        assert not p.tool_allowed_in_phase("rollback_pipeline", Phase.OBSERVE)


