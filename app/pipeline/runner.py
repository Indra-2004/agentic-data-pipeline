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


