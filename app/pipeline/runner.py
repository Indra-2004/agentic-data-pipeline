"""Lightweight pipeline runner.

Executes a typed :class:`Pipeline`'s stages in dependency order over a Polars
DataFrame, validating each stage's output against its declared output schema and
optionally persisting per-stage results to the warehouse under a namespace.

The runner is intentionally small and dependency-free (no Airflow/Kafka): a
pipeline is just an ordered list of stage transforms with schema boundaries.
Support for breaking into a real orchestrator later can be an adapter.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import polars as pl

from app.data.schema import compare_schemas
from app.models import Pipeline, SchemaDefinition
from app.pipeline.schemas import infer_schema
from app.pipeline.stages import TransformationError, get_stage_transform
from app.storage.base import Warehouse


class PipelineRunError(Exception):
    """Raised when a stage fails or a schema boundary is violated."""


@dataclass
class StageResult:
    stage_id: str
    ok: bool
    input_rows: int = 0
    output_rows: int = 0
    error: str | None = None
    drift_events: list = field(default_factory=list)
    output_df: pl.DataFrame | None = None


@dataclass
class RunResult:
    pipeline_id: str
    ok: bool
    stages: list[StageResult] = field(default_factory=list)
    final_df: pl.DataFrame | None = None
    error: str | None = None

    def failed_stages(self) -> list[StageResult]:
        return [s for s in self.stages if not s.ok]

    def first_stage(self) -> StageResult | None:
        return self.stages[0] if self.stages else None


