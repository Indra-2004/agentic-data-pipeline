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


