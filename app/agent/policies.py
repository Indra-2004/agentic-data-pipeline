"""Action policies and safety classification.

The policy engine decides whether any action is permitted and whether a fix may
be staged/deployed. The LLM (or any agent reasoning) never makes this decision
directly: it only produces a declarative :class:`FixProposal`, and the policy
engine classifies it and gates execution.

Risk-based approval rules (per spec):
  - LOW    : safe type coercion / non-breaking column addition -> auto-stage
  - MEDIUM : row filtering / column rename -> require approval
  - HIGH   : data deletion / large row-count change / prod schema mutation
             -> require approval + explicit confirmation
"""

from __future__ import annotations

from enum import Enum

from app.models import ApprovalStatus, FixOperationType, FixProposal, RiskLevel
from app.models.state import Phase


class ActionClass(str, Enum):
    READ_ONLY = "READ_ONLY"
    SHADOW_WRITE = "SHADOW_WRITE"
    STAGING_WRITE = "STAGING_WRITE"
    PRODUCTION_WRITE = "PRODUCTION_WRITE"
    ROLLBACK = "ROLLBACK"


# Tools the agent may call, mapped to their safety class. This mapping is the
# single source of truth for "can this tool touch production?"
TOOL_ACTION_CLASS: dict[str, ActionClass] = {
    # schema
    "get_expected_schema": ActionClass.READ_ONLY,
    "get_observed_schema": ActionClass.READ_ONLY,
    "compare_schemas": ActionClass.READ_ONLY,
    "get_schema_history": ActionClass.READ_ONLY,
    # data
    "profile_dataset": ActionClass.READ_ONLY,
    "query_dataset": ActionClass.READ_ONLY,
    "sample_rows": ActionClass.READ_ONLY,
    "run_quality_checks": ActionClass.READ_ONLY,
    "compare_distributions": ActionClass.READ_ONLY,
    "get_metric_history": ActionClass.READ_ONLY,
    # pipeline
    "get_pipeline": ActionClass.READ_ONLY,
    "get_pipeline_run": ActionClass.READ_ONLY,
    "get_stage_logs": ActionClass.READ_ONLY,
    "get_lineage": ActionClass.READ_ONLY,
    "run_stage": ActionClass.SHADOW_WRITE,
    # fix
    "propose_transformation": ActionClass.READ_ONLY,
    "validate_transformation": ActionClass.SHADOW_WRITE,
    "create_pipeline_version": ActionClass.STAGING_WRITE,
    # deployment
    "stage_pipeline": ActionClass.STAGING_WRITE,
    "run_canary": ActionClass.PRODUCTION_WRITE,
    "monitor_canary": ActionClass.READ_ONLY,
    "rollback_pipeline": ActionClass.ROLLBACK,
}

# Which phases are allowed to invoke a given action class.
_PHASE_ACTION_ALLOW: dict[Phase, set[ActionClass]] = {
    Phase.OBSERVE: {ActionClass.READ_ONLY},
    Phase.DETECT: {ActionClass.READ_ONLY},
    Phase.DIAGNOSE: {ActionClass.READ_ONLY},
    Phase.PLAN: {ActionClass.READ_ONLY},
    Phase.PROPOSE: {ActionClass.READ_ONLY},
    Phase.VALIDATE: {ActionClass.SHADOW_WRITE, ActionClass.READ_ONLY},
    Phase.APPROVAL: {ActionClass.READ_ONLY},
    Phase.STAGE: {ActionClass.STAGING_WRITE, ActionClass.READ_ONLY},
    Phase.CANARY: {ActionClass.PRODUCTION_WRITE, ActionClass.READ_ONLY},
    Phase.MONITOR: {ActionClass.READ_ONLY},
    Phase.ROLLBACK: {ActionClass.ROLLBACK, ActionClass.READ_ONLY},
    Phase.SUCCESS: set(),
    Phase.SAFE_STOP: set(),
}


class PolicyError(Exception):
    """Raised when a tool call or fix is not permitted."""


