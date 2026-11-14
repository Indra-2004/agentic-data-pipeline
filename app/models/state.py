"""Agent triage state machine phase and status enums, plus the full state model."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from app.models.fix import FixProposal, ValidationReport
from app.models.quality import QualityAnomaly
from app.models.schema import DriftEvent


