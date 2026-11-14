"""Tests for the LLM providers: DeterministicLLM and OpenAIProvider (mocked)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.agent.llm import DeterministicLLM, OpenAIProvider, create_llm
from app.models import (
    DataType,
    DriftEvent,
    DriftEventType,
    FixOperationType,
    QualityAnomaly,
    RiskLevel,
)
from app.agent import policies  # noqa: F401 (ensure policy package imports)


def _type_drift() -> DriftEvent:
    return DriftEvent(
        type=DriftEventType.TYPE_CHANGED,
        column="amount",
        expected=DataType.DOUBLE.value,
        observed=DataType.VARCHAR.value,
    )


class TestDeterministicLLM:
    @pytest.mark.asyncio
    async def test_type_drift_proposes_cast(self):
        llm = DeterministicLLM()
        proposal = await llm.build_proposal(
            drift_events=[_type_drift()],
            quality_anomalies=[],
            hypotheses=[],
            pipeline_context={},
        )
        assert proposal is not None
        assert proposal.operations[0].operation == FixOperationType.CAST_TYPE
        assert proposal.operations[0].column == "amount"
        assert proposal.operations[0].to_type == "DOUBLE"
        assert proposal.risk == RiskLevel.LOW

    @pytest.mark.asyncio
    async def test_null_spike_proposes_default_value(self):
        llm = DeterministicLLM()
        proposal = await llm.build_proposal(
            drift_events=[],
            quality_anomalies=[
                QualityAnomaly(metric="null_rate", column="amount", observed=0.22)
            ],
            hypotheses=[],
            pipeline_context={},
        )
        assert proposal is not None
        assert any(
            o.operation == FixOperationType.DEFAULT_VALUE and o.column == "amount"
            for o in proposal.operations
        )

    @pytest.mark.asyncio
    async def test_no_evidence_returns_none(self):
        llm = DeterministicLLM()
        assert llm.name() == "deterministic"
        proposal = await llm.build_proposal(
            drift_events=[], quality_anomalies=[], hypotheses=[], pipeline_context={}
        )
        assert proposal is None


