"""Safety test suite: adversarial properties with white-box assertions.

These complement the evaluation tests. Here we assert the *system* properties
directly: what the agent may write, when it may write it, and that the warehouse
is untouched whenever a proposal is unsafe.
"""

from __future__ import annotations

import pytest

from app.agent.llm import DeterministicLLM
from app.agent.orchestrator import Orchestrator, TriageConfig
from app.evaluation.runner import _fresh_ctx, build_environment
from app.models import ApprovalStatus, RiskLevel
from app.models.state import DeploymentStatus, Phase


