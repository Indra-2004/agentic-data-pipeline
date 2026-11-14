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


class LLMProvider(ABC):
    @abstractmethod
    async def build_proposal(self, **kwargs: Any) -> FixProposal | None:
        raise NotImplementedError


# --- Deterministic, rule-based implementation ---


def _propose_cast(event: DriftEvent) -> FixOperation:
    # Cast the drifted (observed) type BACK to the expected type.
    target = event.expected or event.observed
    if target in (None, DataType.UNKNOWN.value):
        target = "DOUBLE"
    # Timestamps cannot be produced by a plain cast of arbitrary strings; the
    # safe operation is an explicit parse.
    if target == DataType.TIMESTAMP.value and event.observed == DataType.VARCHAR.value:
        return FixOperation(
            operation=FixOperationType.PARSE_TIMESTAMP,
            column=event.column,
            target=None,
        )
    return FixOperation(
        operation=FixOperationType.CAST_TYPE,
        column=event.column,
        to_type=target,
        on_error=OnError.NULL,
    )


