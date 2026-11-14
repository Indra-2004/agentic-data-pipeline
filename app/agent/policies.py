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


