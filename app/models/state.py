"""Agent triage state machine phase and status enums, plus the full state model."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from app.models.fix import FixProposal, ValidationReport
from app.models.quality import QualityAnomaly
from app.models.schema import DriftEvent


class Phase(str, Enum):
    """Bounded state machine phases (mirrors the spec's core agent loop)."""

    OBSERVE = "OBSERVE"
    DETECT = "DETECT"
    DIAGNOSE = "DIAGNOSE"
    PLAN = "PLAN"
    PROPOSE = "PROPOSE"
    VALIDATE = "VALIDATE"
    APPROVAL = "APPROVAL"
    STAGE = "STAGE"
    CANARY = "CANARY"
    MONITOR = "MONITOR"
    SUCCESS = "SUCCESS"
    ROLLBACK = "ROLLBACK"
    SAFE_STOP = "SAFE_STOP"


class ApprovalStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_APPROVED = "auto_approved"


class DeploymentStatus(str, Enum):
    NOT_DEPLOYED = "not_deployed"
    STAGED = "staged"
    CANARY_RUNNING = "canary_running"
    ACTIVE = "active"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


class Hypothesis(BaseModel):
    id: str
    description: str
    confidence: float = 0.0
    evidence: list[str] = Field(default_factory=list)
    is_selected: bool = False
    fix_hint: FixProposal | None = None


