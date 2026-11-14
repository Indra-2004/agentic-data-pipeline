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


@pytest.fixture()
def env():
    return build_environment()


async def _run_with_ctx(scenario, env):
    """Run a scenario against an accessible context (white-box)."""
    ctx, pipeline = _fresh_ctx(env)
    if scenario.seed_metrics is not None:
        await scenario.seed_metrics(ctx.store.metadata)
    if scenario.id == "partial_deployment_failure":
        table = pipeline.stages[0].name
        await ctx.store.warehouse.write_table(table, "main:v1.0", env.healthy)
    drifted = scenario.build(env.healthy)
    orch = Orchestrator(
        ctx=ctx, llm=DeterministicLLM(), config=TriageConfig(approval_mode="auto")
    )
    if scenario.setup is not None:
        scenario.setup(orch, scenario.id)
    state = await orch.run(pipeline.id, drifted)
    return state, ctx


