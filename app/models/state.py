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


