"""Unit tests for the pipeline package: stages, fixes, runner, registry."""

from __future__ import annotations

import json

import polars as pl
import pytest

from app.models import (
    ColumnDefinition,
    DataType,
    FixOperation,
    FixOperationType,
    OnError,
    Pipeline,
    PipelineStage,
    SchemaDefinition,
)
from app.pipeline.registry import PipelineRegistry
from app.pipeline.runner import run_pipeline
from app.pipeline.stages import (
    TransformationError,
    apply_fix_operations,
    list_stage_transforms,
    op_cast_type,
    op_parse_timestamp,
)
from app.storage import MemoryWarehouse


