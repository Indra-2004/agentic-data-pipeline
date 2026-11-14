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


