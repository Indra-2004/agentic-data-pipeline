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


class TestProfiler:
    def test_profile_numeric(self):
        df = pl.DataFrame({"amount": [1.0, 2.0, 3.0]})
        p = profile_dataset(df)
        assert p["row_count"] == 3
        prof = p["profiles"]["amount"]
        assert prof["mean"] == 2.0
        assert prof["null_rate"] == 0.0
        assert prof["dtype"] == "Float64"

    def test_profiler_null_rate(self):
        df = pl.DataFrame({"a": [1.0, None, None, 4.0]})
        p = profile_dataset(df)["profiles"]["a"]
        assert p["null_count"] == 2
        assert p["null_rate"] == pytest.approx(0.5)

    def test_row_count(self):
        assert row_count(pl.DataFrame({"x": [1, 2, 3, 4]})) == 4


