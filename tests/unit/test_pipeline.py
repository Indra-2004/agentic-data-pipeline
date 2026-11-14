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


def _orders_schema(v: int = 3, amount: DataType = DataType.DOUBLE) -> SchemaDefinition:
    return SchemaDefinition(
        table="orders",
        version=v,
        columns=[
            ColumnDefinition(name="order_id", type=DataType.INTEGER),
            ColumnDefinition(name="amount", type=amount),
            ColumnDefinition(name="currency", type=DataType.VARCHAR),
        ],
    )


class TestSchemaInference:
    def test_cast_type_fix(self):
        op = FixOperation(
            operation=FixOperationType.CAST_TYPE,
            column="amount",
            to_type="DOUBLE",
            on_error=OnError.REJECT,
        )
        df = pl.DataFrame({"order_id": [1, 2], "amount": ["10.5", "20.0"]})
        out = apply_fix_operations(df, [op])
        assert out["amount"].dtype.is_float()
        assert out["amount"].to_list() == [10.5, 20.0]

    def test_rename_and_timestamp(self):
        df = pl.DataFrame(
            {
                "user_id": [1, 2],
                "ts": ["2024-01-01 10:00:00", "2024-01-02 10:00:00"],
            }
        )
        ops = [
            FixOperation(
                operation=FixOperationType.RENAME_COLUMN,
                column="user_id",
                target="customer_id",
            ),
            FixOperation(operation=FixOperationType.PARSE_TIMESTAMP, column="ts"),
        ]
        out = apply_fix_operations(df, ops)
        assert "customer_id" in out.columns
        assert "user_id" not in out.columns
        assert out["ts"].dtype == pl.Datetime

    def test_fill_null_and_deduplicate(self):
        df = pl.DataFrame({"a": [1, 1, 2, None, 3], "b": [1, 1, 2, None, 3]})
        ops = [
            FixOperation(
                operation=FixOperationType.FILL_NULL, column="b", value=0
            ),
            FixOperation(operation=FixOperationType.DEDUPLICATE),
        ]
        out = apply_fix_operations(df, ops)
        assert out["b"].null_count() == 0
        assert out.height == df.unique().height

    def test_normalize_and_column_mapping(self):
        df = pl.DataFrame(
            {"code": ["  USD  ", " EUR ", ""], "status": ["A", "B", "C"]}
        )
        ops = [
            FixOperation(
                operation=FixOperationType.NORMALIZE_STRING,
                column="code",
                target="strip",
            ),
            FixOperation(
                operation=FixOperationType.COLUMN_MAPPING,
                column="status",
                value={"A": "active", "B": "blocked", "C": "closed"},
            ),
        ]
        out = apply_fix_operations(df, ops)
        assert out["code"].to_list() == ["USD", "EUR", ""]
        assert out["status"].to_list() == ["active", "blocked", "closed"]

    def test_default_value_replaces_empty(self):
        df = pl.DataFrame({"tier": [None, "", "gold"]})
        out = apply_fix_operations(
            df,
            [FixOperation(operation=FixOperationType.DEFAULT_VALUE, column="tier", value="standard")],
        )
        assert out["tier"].null_count() == 0
        assert out["tier"].to_list() == ["standard", "standard", "gold"]


class TestStageOps:
    def test_cast_drop(self):
        df = pl.DataFrame({"amount": ["1.0", "2.0", "bad", "3.0"]})
        out = op_cast_type(df, "amount", "DOUBLE", on_error=OnError.DROP)
        assert out.height == 3
        assert out["amount"].dtype.is_float()

    def test_cast_null(self):
        df = pl.DataFrame({"amount": ["1.0", "bad", "3.0"]})
        out = op_cast_type(df, "amount", "DOUBLE", on_error=OnError.NULL)
        assert out.height == 3
        assert out["amount"].null_count() == 1

    def test_cast_reject_raises(self):
        df = pl.DataFrame({"amount": ["1.0", "bad"]})
        with pytest.raises(TransformationError):
            op_cast_type(df, "amount", "DOUBLE", on_error=OnError.REJECT)

    def test_parse_timestamp(self):
        df = pl.DataFrame({"ts": ["2024-01-01", "2024-01-02"]})
        out = op_parse_timestamp(df, "ts")
        assert out["ts"].dtype in (pl.Datetime, pl.Date)

    def test_known_stage_transforms(self):
        names = list_stage_transforms()
        assert "clean_orders" in names
        assert "aggregate_daily_revenue" in names


