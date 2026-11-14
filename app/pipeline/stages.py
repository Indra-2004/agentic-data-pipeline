"""Pipeline stage transformations.

Contains the *constrained* set of safe transformations the engine is allowed to
apply. These same operations back both named pipeline stages (via the
``transformation`` registry) and declarative fix proposals. Arbitrary SQL is
deliberately not supported: each operation is a small, reviewed Polars
transformation.
"""

from __future__ import annotations

from typing import Any, Callable

import polars as pl

from app.models import DataType, FixOperation, FixOperationType, OnError
from app.pipeline.schemas import logical_to_polars


class TransformationError(Exception):
    """Raised when a transformation cannot be applied safely."""


# --- Primitive operations (used by fix proposals) ---


def op_cast_type(
    df: pl.DataFrame, column: str, to: str, on_error: OnError = OnError.REJECT
) -> pl.DataFrame:
    try:
        data_type = DataType(to)
    except ValueError as exc:
        raise TransformationError(f"Unknown target type {to!r}") from exc
    target = logical_to_polars(data_type)
    series = df[column]

    if on_error == OnError.REJECT:
        try:
            cast = series.cast(target, strict=True)
        except Exception as exc:
            raise TransformationError(
                f"Cannot cast {column} to {to}: {exc}"
            ) from exc
        return df.with_columns(cast.alias(column))

    # NULL / DROP: non-strict cast turns invalid values into nulls
    cast = series.cast(target, strict=False)
    if on_error == OnError.DROP:
        return df.with_columns(cast.alias(column)).filter(
            pl.col(column).is_not_null()
        )
    return df.with_columns(cast.alias(column))


def op_fill_null(df: pl.DataFrame, column: str, value: Any) -> pl.DataFrame:
    return df.with_columns(df[column].fill_null(value).alias(column))


def op_deduplicate(df: pl.DataFrame) -> pl.DataFrame:
    return df.unique()


def op_normalize_string(
    df: pl.DataFrame, column: str, *, lower: bool = False, strip: bool = True
) -> pl.DataFrame:
    expr = pl.col(column)
    if strip:
        expr = expr.str.strip_chars()
    if lower:
        expr = expr.str.to_lowercase()
    return df.with_columns(expr.alias(column))


