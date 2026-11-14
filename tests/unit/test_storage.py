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


