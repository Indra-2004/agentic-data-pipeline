"""Unit tests for the storage layer: both backends (in-memory + SQLite)."""

from __future__ import annotations

import polars as pl
import pytest

from app.models import (
    ColumnDefinition,
    DataType,
    DriftEvent,
    DriftEventType,
    Phase,
    Pipeline,
    PipelineStage,
    PipelineTriageState,
    SchemaDefinition,
    Severity,
)
from app.storage import (
    MemoryMetadataStore,
    MemoryWarehouse,
    SQLiteMetadataStore,
    SQLiteWarehouse,
    create_store,
)


def _orders_schema(version: int = 3) -> SchemaDefinition:
    return SchemaDefinition(
        table="orders",
        version=version,
        columns=[
            ColumnDefinition(name="order_id", type=DataType.INTEGER),
            ColumnDefinition(name="amount", type=DataType.DOUBLE),
            ColumnDefinition(name="currency", type=DataType.VARCHAR),
        ],
    )


def _orders_pipeline() -> Pipeline:
    stage = PipelineStage(
        id="orders_clean",
        name="Orders Clean",
        input_schema=_orders_schema(),
        output_schema=_orders_schema(version=4),
        transformation="clean_orders",
    )
    return Pipeline(
        id="orders",
        name="Orders Pipeline",
        version="1.0",
        source="fixtures:orders.csv",
        stages=[stage],
    )


def _sample_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "order_id": [1, 2, 3, 4],
            "amount": [49.99, 12.0, 99.0, 4.5],
            "currency": ["USD", "USD", "EUR", "GBP"],
        }
    )


