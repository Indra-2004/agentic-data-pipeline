"""In-memory storage backend.

Used by unit/integration tests and fast deterministic demo runs. Implements the
same :class:`MetadataStore` / :class:`Warehouse` protocols as SQLite without any
filesystem or process dependency.
"""

from __future__ import annotations

from typing import Any

import polars as pl

from app.models import Pipeline, PipelineTriageState
from app.models.quality import QualityReport
from app.models.schema import DriftEvent, SchemaDefinition
from app.storage.base import MetadataStore, Warehouse


