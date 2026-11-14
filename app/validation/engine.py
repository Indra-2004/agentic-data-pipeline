"""Shadow validation engine.

Compares the *current* pipeline output against the *candidate* (fixed) output on
the same observed data, producing a :class:`ValidationReport`. Used before any
deployment.

Two cases:
  - Current is healthy         -> delta checks (row count, aggregates, quality).
  - Current is broken (drift)  -> validate candidate against the pipeline's
    declared output schema and absolute invariants (schema, quality, no data
    loss vs input row count, non-negative business metrics).

The candidate must never be allowed to silently destroy data or corrupt metrics.
"""

from __future__ import annotations

import polars as pl

from app.models import SchemaDefinition, ValidationCheck, ValidationReport, ValidationStatus
from app.pipeline.runner import RunResult
from app.pipeline.schemas import infer_schema

# Conventional business-metric aliases: aggregated output column -> source
# input column. Used to compare a candidate's business metric against the raw
# input even when the current pipeline is broken (no healthy baseline).
BUSINESS_ALIASES = {"revenue": "amount", "total_revenue": "amount", "total": "amount"}


