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


