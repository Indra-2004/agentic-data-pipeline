"""Tool-layer tests: every registered tool works through the policy-gated registry."""

from __future__ import annotations

import pytest

from app.agent.policies import PolicyEngine, PolicyError
from app.evaluation.runner import _fresh_ctx, build_environment
from app.models.state import ApprovalStatus, Phase
from app.tools.registry import ToolRegistry


@pytest.fixture()
def setup():
    env = build_environment()
    ctx, pipeline = _fresh_ctx(env)
    ctx.observed[pipeline.id] = env.healthy
    registry = ToolRegistry(ctx, PolicyEngine(approval_mode="auto"))
    return ctx, pipeline, registry


