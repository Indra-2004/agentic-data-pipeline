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


def _ctx(pipeline):
    store = BackendStore(MemoryMetadataStore(), MemoryWarehouse())
    lineage = LineageGraph(
        [
            LineageEdge("orders", "clean.orders", ["order_id", "amount", "currency"]),
            LineageEdge("clean.orders", "daily_revenue", ["amount"]),
        ]
    )
    return ToolContext(store=store, pipelines={pipeline.id: pipeline}, lineage=lineage)


class TestHealthyFixture:
    @pytest.mark.asyncio
    async def test_healthy_data_is_not_mutated(self):
        pipeline = _orders_pipeline()
        ctx = _ctx(pipeline)
        orch = Orchestrator(ctx=ctx, llm=DeterministicLLM(), config=TriageConfig())
        state = await orch.run(pipeline.id, _healthy_df())
        # No drift/anomaly -> no destructive action, no deployment.
        assert state.detected_issues == []
        assert state.phase == Phase.SAFE_STOP
        assert state.deployment_status.value == "not_deployed"

    @pytest.mark.asyncio
    async def test_runner_persists_to_shadow_namespace(self):
        pipeline = _orders_pipeline()
        store = BackendStore(MemoryMetadataStore(), MemoryWarehouse())
        df = _healthy_df()
        res = await run_pipeline(pipeline, df, store.warehouse, namespace="shadow")
        assert res.ok is True
        versions = await store.warehouse.list_versions("daily_revenue")
        assert versions == ["shadow:v1.0"]


