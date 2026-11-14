"""Tool-layer tests: every registered tool works through the policy-gated registry."""

from __future__ import annotations

import pytest

from app.agent.policies import PolicyEngine, PolicyError
from app.evaluation.runner import _fresh_ctx, build_environment
from app.models.state import ApprovalStatus, Phase
from app.tools.registry import ToolRegistry


