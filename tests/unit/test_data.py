"""Unit tests for the data layer: profiler, schema comparison, quality, anomaly, lineage."""

from __future__ import annotations

import polars as pl
import pytest

from app.data.anomaly import detect_anomalies
from app.data.lineage import LineageEdge, LineageGraph
from app.data.profiler import profile_dataset, row_count
from app.data.quality import run_quality_checks
from app.data.schema import compare_schemas, compute_rename_hypotheses
from app.models import (
    ColumnDefinition,
    DataType,
    DriftEventType,
    SchemaDefinition,
)
from app.pipeline.schemas import infer_schema, polars_to_logical


def _orders_expected() -> SchemaDefinition:
    return SchemaDefinition(
        table="orders",
        version=3,
        columns=[
            ColumnDefinition(name="order_id", type=DataType.INTEGER),
            ColumnDefinition(name="amount", type=DataType.DOUBLE),
            ColumnDefinition(name="currency", type=DataType.VARCHAR),
        ],
    )


