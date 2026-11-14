"""Schema definition and drift event models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class DataType(str, Enum):
    """Canonical logical types used across the schema registry.

    These map onto Polars/warehouse physical types but stay engine-agnostic so
    the schema registry can grow DuckDB/Postgres adapters later.
    """

    INTEGER = "INTEGER"
    DOUBLE = "DOUBLE"
    VARCHAR = "VARCHAR"
    BOOLEAN = "BOOLEAN"
    TIMESTAMP = "TIMESTAMP"
    DATE = "DATE"
    DECIMAL = "DECIMAL"
    UNKNOWN = "UNKNOWN"


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ColumnDefinition(BaseModel):
    name: str
    type: DataType
    nullable: bool = False
    description: str | None = None


