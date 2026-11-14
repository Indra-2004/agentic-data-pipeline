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


