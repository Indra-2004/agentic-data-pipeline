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


class DeterministicLLM(LLMProvider):
    """Rule-based proposal builder; no network, fully deterministic.

    Maps each detected issue to the minimal safe declarative operation, and
    infers risk/confidence from severity and data-loss potential. Used to keep
    scenarios reproducible and to guarantee the system runs without a key.
    """

    def name(self) -> str:
        return "deterministic"

    async def build_proposal(
        self,
        *,
        drift_events: list[DriftEvent],
        quality_anomalies: list[QualityAnomaly],
        hypotheses: list[str],
        pipeline_context: dict[str, Any],
    ) -> FixProposal | None:
        ops: list[FixOperation] = []
        evidence: list[str] = []

        for e in drift_events:
            evidence.append(
                f"{e.column}: {e.expected} -> {e.observed} ({e.type.value})"
            )
            if e.type == DriftEventType.TYPE_CHANGED:
                ops.append(_propose_cast(e))
            elif e.type == DriftEventType.COLUMN_ADDED:
                # Non-breaking; no operation required for the pipeline to run.
                evidence.append(f"new column {e.column} tolerated: NULLABLE")
            elif e.type == DriftEventType.COLUMN_REMOVED:
                # Blocking drift: cannot silently fabricate a column.
                evidence.append(
                    f"column {e.column} removed; propose drop_invalid_rows only "
                    "after explicit confirmation"
                )
            elif e.type == DriftEventType.NULLABLE_CHANGED:
                evidence.append(f"nullability change on {e.column} acceptable")

        for a in quality_anomalies:
            evidence.append(
                f"{a.metric}:{a.column or ''} observed={a.observed} expected={a.expected}"
            )
            if a.metric == "duplicate_rate" and a.observed and a.observed > 0.01:
                ops.append(FixOperation(operation=FixOperationType.DEDUPLICATE))
            elif a.metric == "null_rate" and a.column:
                ops.append(
                    FixOperation(
                        operation=FixOperationType.DEFAULT_VALUE,
                        column=a.column,
                        value=0,
                    )
                )
            elif a.metric == "referential_integrity" and a.column:
                ops.append(
                    FixOperation(
                        operation=FixOperationType.DROP_INVALID_ROWS,
                        column=a.column,
                    )
                )

        if not ops:
            return None

        # Risk: block (deletion-heavy) fixes from auto-run unless explicit.
        has_drop = any(
            o.operation
            in (FixOperationType.DROP_INVALID_ROWS, FixOperationType.DEDUPLICATE)
            for o in ops
        )
        has_cast = any(o.operation == FixOperationType.CAST_TYPE for o in ops)
        if has_drop and has_cast:
            risk = RiskLevel.HIGH
            confidence = 0.6
        elif has_drop:
            risk = RiskLevel.MEDIUM
            confidence = 0.7
        else:
            risk = RiskLevel.LOW
            confidence = 0.92

        root_cause = (
            "Schema drift detected ("
            + "; ".join(evidence[:4])
            + ")"
            if drift_events
            else "Data-quality anomalies require remediation"
        )

        return FixProposal(
            root_cause=root_cause,
            evidence=evidence,
            operations=ops,
            affected_stages=list(pipeline_context.get("affected_stages", [])),
            affected_columns=sorted({o.column for o in ops if o.column}),
            expected_impact="Brings observed data into expected schema and quality.",
            risk=risk,
            confidence=confidence,
            validation_plan=[
                "schema",
                "row_count",
                "null_rate",
                "duplicate_rate",
                "aggregates",
            ],
            rollback_strategy="restore previous active pipeline version",
        )


# --- OpenAI implementation (tested via mock) ---


