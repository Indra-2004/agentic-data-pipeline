"""Schema comparison engine: deterministic drift detection.

Detects additions, removals, type changes, nullability changes and produces
*rename hypotheses* (never treated as fact) using name/type/value similarity.
"""

from __future__ import annotations

from difflib import SequenceMatcher

import polars as pl

from app.models import (
    DriftEvent,
    DriftEventType,
    RenameHypothesis,
    SchemaDefinition,
    Severity,
)


def compare_schemas(
    expected: SchemaDefinition, observed: SchemaDefinition
) -> list[DriftEvent]:
    """Compare expected vs observed, returning a list of drift events."""
    exp_map = expected.column_map
    obs_map = observed.column_map
    exp_names = set(exp_map)
    obs_names = set(obs_map)

    events: list[DriftEvent] = []

    for name in sorted(obs_names - exp_names):
        events.append(
            DriftEvent(
                type=DriftEventType.COLUMN_ADDED,
                column=name,
                observed=obs_map[name].type.value,
                severity=Severity.LOW,
            )
        )

    for name in sorted(exp_names - obs_names):
        events.append(
            DriftEvent(
                type=DriftEventType.COLUMN_REMOVED,
                column=name,
                expected=exp_map[name].type.value,
                severity=Severity.MEDIUM,
            )
        )

    for name in sorted(exp_names & obs_names):
        e = exp_map[name]
        o = obs_map[name]
        if e.type != o.type:
            events.append(
                DriftEvent(
                    type=DriftEventType.TYPE_CHANGED,
                    column=name,
                    expected=e.type.value,
                    observed=o.type.value,
                    severity=Severity.HIGH,
                )
            )
        if e.nullable != o.nullable:
            events.append(
                DriftEvent(
                    type=DriftEventType.NULLABLE_CHANGED,
                    column=name,
                    expected=str(e.nullable),
                    observed=str(o.nullable),
                    severity=Severity.MEDIUM,
                )
            )

    return events


