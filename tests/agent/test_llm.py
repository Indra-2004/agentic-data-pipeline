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


