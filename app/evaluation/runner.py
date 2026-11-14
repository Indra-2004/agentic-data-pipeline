"""Evaluation runner: executes scenarios through the real orchestrator and scores them.

Every scenario runs against an isolated in-memory store with the real pipeline
definition loaded from ``pipelines/``. Safety scenarios run through ``setup``
hooks that inject the adversarial condition (a malicious LLM or a forced canary
failure). The headline metric is data loss, which must be zero everywhere.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import polars as pl

from app.agent.llm import DeterministicLLM
from app.agent.orchestrator import Orchestrator, TriageConfig
from app.data.lineage import LineageEdge, LineageGraph
from app.data.loader import load_source
from app.evaluation.models import ExpectedOutcome, Scenario, ScenarioResult
from app.models import DeploymentStatus, FixOperationType
from app.pipeline.registry import PipelineRegistry
from app.storage import BackendStore, MemoryMetadataStore, MemoryWarehouse
from app.tools.context import make_context


ROW_DROP_OPS = {FixOperationType.DROP_INVALID_ROWS}


@dataclass
class EvalEnvironment:
    pipeline_id: str
    healthy: pl.DataFrame
    customers: pl.DataFrame


def build_environment() -> EvalEnvironment:
    pipeline = PipelineRegistry("./pipelines").get("orders")
    healthy = load_source("fixtures:orders.csv", "./datasets/fixtures")
    customers = load_source("fixtures:customers.csv", "./datasets/fixtures")
    return EvalEnvironment(pipeline_id=pipeline.id, healthy=healthy, customers=customers)


def _fresh_ctx(env: EvalEnvironment):
    store = BackendStore(MemoryMetadataStore(), MemoryWarehouse())
    lineage = LineageGraph(
        [
            LineageEdge("orders", "clean.orders", ["order_id", "amount", "currency"]),
            LineageEdge("clean.orders", "daily_revenue", ["amount"]),
        ]
    )
    pipeline = PipelineRegistry("./pipelines").get("orders")
    ctx = make_context(
        store=store,
        pipelines={pipeline.id: pipeline},
        lineage=lineage,
        references={"customer_id": env.customers},
    )
    return ctx, pipeline


