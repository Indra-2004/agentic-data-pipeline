"""Storage protocols.

The system separates two concerns, each behind a protocol so the concrete
backends (SQLite, in-memory, and later DuckDB/Postgres) are swappable:

- ``MetadataStore``: persists agent triage state, pipeline runs, schema
  registry versions, quality/anomaly metric history, lineage edges and
  rollback records. This is what makes the agent *resumable*.
- ``Warehouse``: stores the actual datasets (Polars DataFrames) keyed by
  ``(table, version)``. Versioned writes give canary deployment and rollback
  a deterministic, idempotent primitive.
"""
from __future__ import annotations

from abc import ABC
from typing import Any, Protocol, runtime_checkable

import polars as pl

from app.models import Pipeline, PipelineTriageState
from app.models.quality import QualityReport
from app.models.schema import DriftEvent, SchemaDefinition


