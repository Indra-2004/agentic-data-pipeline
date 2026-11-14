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


def _ctx() -> ToolContext:
    store = BackendStore(MemoryMetadataStore(), MemoryWarehouse())
    lineage = LineageGraph([
        LineageEdge("orders", "clean.orders", ["order_id", "amount", "currency"]),
        LineageEdge("clean.orders", "daily_revenue", ["amount"]),
    ])
    return ToolContext(store=store, pipelines={"orders": _pipeline()}, lineage=lineage)


def _drifted_df(n: int = 100) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "order_id": list(range(n)),
            "amount": [str(10 + i * 0.5) for i in range(n)],
            "currency": ["USD" if i % 3 else "EUR" for i in range(n)],
        }
    )


class TestTypeDriftPromotion:
    @pytest.mark.asyncio
    async def test_drift_reaches_success(self):
        ctx = _ctx()
        orch = Orchestrator(ctx=ctx, llm=DeterministicLLM(), config=TriageConfig(approval_mode="auto"))
        state = await orch.run("orders", _drifted_df())

        assert state.phase == Phase.SUCCESS
        assert state.deployment_status == DeploymentStatus.ACTIVE
        assert any(e.column == "amount" for e in state.detected_issues)
        assert state.validation_report is not None and state.validation_report.passed
        assert state.approval_status == ApprovalStatus.AUTO_APPROVED
        # State is persisted/resumable.
        assert await ctx.store.metadata.load_state(state.run_id) is not None

    @pytest.mark.asyncio
    async def test_state_phase_transitions_recorded(self):
        ctx = _ctx()
        orch = Orchestrator(ctx=ctx, llm=DeterministicLLM(), config=TriageConfig())
        state = await orch.run("orders", _drifted_df())
        assert state.phase == Phase.SUCCESS
        # Proposed fix cast the drifted type back to DOUBLE.
        assert state.proposed_fix is not None
        assert state.proposed_fix.operations[0].operation == FixOperationType.CAST_TYPE


