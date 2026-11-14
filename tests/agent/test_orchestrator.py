"""End-to-end orchestrator tests: bounded state machine behavior."""

from __future__ import annotations

import polars as pl
import pytest

from app.agent.llm import DeterministicLLM
from app.agent.orchestrator import Orchestrator, TriageConfig
from app.data.lineage import LineageEdge, LineageGraph
from app.models import (
    ColumnDefinition,
    DataType,
    FixOperation,
    FixOperationType,
    Pipeline,
    PipelineStage,
    SchemaDefinition,
)
from app.models.state import ApprovalStatus, DeploymentStatus, Phase
from app.storage import BackendStore, MemoryMetadataStore, MemoryWarehouse
from app.tools.context import ToolContext


