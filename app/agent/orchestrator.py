"""Agent orchestrator: the bounded state machine.

Implements the spec's core agent loop as an explicit, bounded state machine:

    OBSERVE -> DETECT -> DIAGNOSE -> PLAN -> PROPOSE -> VALIDATE -> APPROVAL
        -> STAGE -> CANARY -> MONITOR -> SUCCESS | ROLLBACK

Guardrails enforced here (no unbounded `while True` LLM loop):
  - max iterations (agent cycle budget)
  - max tool calls (attempt budget)
  - execution timeout (asyncio)
  - resource budget (observed row/byte caps)

The agent never decides whether a production action is permitted: every tool call
is gated by the :class:`PolicyEngine`. The LLM only *produces* a declarative
:class:`FixProposal`; the policy classifies its risk and gates deployment.
State is persisted on every phase transition, making a run resumable by run_id.
"""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import Callable

import polars as pl

from app.agent.diagnosis import DiagnosisEngine
from app.agent.llm import LLMProvider
from app.agent.policies import PolicyEngine
from app.agent.planner import Planner
from app.data.anomaly import detect_anomalies
from app.data.schema import compare_schemas
from app.data.quality import run_quality_checks
from app.models import (
    ApprovalStatus,
    DeploymentStatus,
    DriftEventType,
    FixProposal,
    PipelineTriageState,
    Phase,
    RiskLevel,
    ValidationReport,
)
from app.pipeline.schemas import infer_schema
from app.observability.metrics import MetricRepository
from app.observability.monitor import HealthMonitor
from app.tools.context import ToolContext
from app.tools.registry import ToolRegistry

ApprovalResolver = Callable[[RiskLevel, FixProposal | None], ApprovalStatus]


