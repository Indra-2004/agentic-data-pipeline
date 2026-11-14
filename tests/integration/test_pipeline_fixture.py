"""Integration tests: full pipeline on real fixtures + shadow validation + rollback."""

from __future__ import annotations

import polars as pl
import pytest

from app.data.loader import load_source
from app.data.lineage import LineageEdge, LineageGraph
from app.models.state import Phase
from app.pipeline.registry import PipelineRegistry
from app.pipeline.runner import run_pipeline
from app.rollback.manager import RollbackManager
from app.storage import MemoryMetadataStore, MemoryWarehouse, BackendStore
from app.tools.context import ToolContext
from app.agent.llm import DeterministicLLM
from app.agent.orchestrator import Orchestrator, TriageConfig
from app.validation.engine import shadow_validate


def _orders_pipeline():
    return PipelineRegistry("./pipelines").get("orders")


def _healthy_df():
    return load_source("fixtures:orders.csv", "./datasets/fixtures")


