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


def _sch(v: int, types) -> SchemaDefinition:
    return SchemaDefinition(
        table="orders", version=v,
        columns=[ColumnDefinition(name=n, type=t) for n, t in types],
    )


def _pipeline() -> Pipeline:
    exp = _sch(3, [("order_id", DataType.INTEGER), ("amount", DataType.DOUBLE), ("currency", DataType.VARCHAR)])
    return Pipeline(
        id="orders", name="Orders", version="1.0", source="x",
        stages=[
            PipelineStage(id="orders_clean", name="clean.orders",
                          input_schema=exp, output_schema=exp,
                          transformation="clean_orders", dependencies=[]),
            PipelineStage(id="daily_revenue", name="daily_revenue",
                          input_schema=exp,
                          output_schema=_sch(1, [("order_id", DataType.INTEGER),
                                                  ("currency", DataType.VARCHAR),
                                                  ("revenue", DataType.DOUBLE)]),
                          transformation="aggregate_daily_revenue",
                          dependencies=["orders_clean"]),
        ],
    )


