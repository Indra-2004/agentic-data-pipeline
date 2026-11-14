"""Minimal FastAPI surface for the Self-Healing Pipeline Agent.

Endpoints:
  GET  /health                          -> liveness + provider/backend info
  GET  /pipelines                       -> registered pipeline definitions
  POST /pipelines/{pipeline_id}/triage  -> run the bounded agent loop on the
                                           pipeline's source data and return the
                                           resulting triage summary
  GET  /runs/{run_id}                   -> full persisted triage state (resumable)

Design notes:
- The agent loop is bounded (iterations, tool calls, timeout) and sub-second on
  demo-scale data, so triage executes within the request and the state is
  persisted for later inspection via ``GET /runs/{run_id}``.
- The LLM provider and storage backend come from settings
  (``SHP_LLM_PROVIDER``, ``SHP_STORAGE_BACKEND``), so the API runs fully
  offline in deterministic mode.
- The app is built via :func:`create_app` so tests can inject overrides.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.agent.llm import create_llm
from app.agent.orchestrator import Orchestrator, TriageConfig
from app.config import settings
from app.data.lineage import LineageEdge, LineageGraph
from app.data.loader import load_source
from app.models import PipelineTriageState
from app.pipeline.registry import PipelineRegistry
from app.storage import store_from_settings
from app.tools.context import make_context


class TriageRequest(BaseModel):
    """Optional overrides for a triage run."""

    source: str | None = Field(
        default=None, description="Source key; defaults to the pipeline's own source."
    )
    limit: int | None = Field(
        default=None, ge=1, description="Cap the number of ingested rows."
    )


class TriageSummary(BaseModel):
    run_id: str
    pipeline_id: str
    phase: str
    deployment_status: str
    final_result: str | None
    detected_issues: list[dict[str, Any]]
    quality_anomalies: list[dict[str, Any]]
    proposed_fix: dict[str, Any] | None
    canary_metrics: dict[str, Any]
    error: str | None


class AppState:
    """Process-wide singletons created during startup."""

    store = None
    registry: PipelineRegistry | None = None
    ctx = None


