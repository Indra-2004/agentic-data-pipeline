"""Declarative fix proposals, safe transformations, and validation reports."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class FixOperationType(str, Enum):
    """The constrained set of safe transformations the engine may apply.

    Arbitrary SQL is deliberately NOT supported. Each operation is declarative
    and translated into a controlled Polars transformation by the engine.
    """

    CAST_TYPE = "cast_type"
    RENAME_COLUMN = "rename_column"
    FILL_NULL = "fill_null"
    DROP_INVALID_ROWS = "drop_invalid_rows"
    NORMALIZE_STRING = "normalize_string"
    PARSE_TIMESTAMP = "parse_timestamp"
    DEDUPLICATE = "deduplicate"
    DEFAULT_VALUE = "default_value"
    COLUMN_MAPPING = "column_mapping"


class OnError(str, Enum):
    REJECT = "reject"
    NULL = "null"
    DROP = "drop"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class FixOperation(BaseModel):
    """A single declarative operation within a fix.

    Example::
        {"operation": "cast_type", "column": "amount", "from": "VARCHAR",
         "to": "DOUBLE", "on_error": "reject"}
    """

    operation: FixOperationType
    column: str | None = None
    target: str | None = None  # rename target / cast target type / etc.
    from_type: str | None = None
    to_type: str | None = None
    value: object | None = None
    on_error: OnError = OnError.REJECT


