"""LLM abstraction for the agent.

Defines :class:`LLMProviderProtocol` and two implementations:

- :class:`DeterministicLLM` — offline, rule-based reproduction of structured
  proposals. Used by default and by evaluation so every scenario is fully
  reproducible without an API key. It translates deterministic evidence
  (drift events + quality anomalies) into a structured :class:`FixProposal`.
- :class:`OpenAIProvider` — thin wrapper over the OpenAI SDK implementing the
  same protocol. Tested via a mock; live use requires an API key in `.env`.

The agent never executes free-form LLM output. The LLM only *produces* a
declarative :class:`FixProposal`; the policy + staging layers decide whether
and how it runs.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable

from app.models import (
    DataType,
    DriftEvent,
    DriftEventType,
    FixOperation,
    FixOperationType,
    FixProposal,
    OnError,
    QualityAnomaly,
    RiskLevel,
)


@runtime_checkable
class LLMProviderProtocol(Protocol):
    async def build_proposal(
        self,
        *,
        drift_events: list[DriftEvent],
        quality_anomalies: list[QualityAnomaly],
        hypotheses: list[str],
        pipeline_context: dict[str, Any],
    ) -> FixProposal | None: ...

    def name(self) -> str: ...


