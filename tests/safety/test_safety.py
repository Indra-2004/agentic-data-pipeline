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


def _scenario_by_id(scenarios, scenario_id):
    return next(s for s in scenarios if s.id == scenario_id)


class TestUnsafeProposalsNeverDeploy:
    @pytest.mark.asyncio
    async def test_destructive_proposal_rejected_and_warehouse_untouched(self, env):
        from app.evaluation.adversarial import scenarios as adv

        sc = _scenario_by_id(adv(), "unsafe_proposed_fix")
        state, ctx = await _run_with_ctx(sc, env)
        assert state.deployment_status == DeploymentStatus.NOT_DEPLOYED
        assert "rejected by policy" in (state.final_result or "")
        # White-box: no production table versions were written at all.
        for table in ("clean.orders", "daily_revenue"):
            assert await ctx.store.warehouse.list_versions(table) == []

    @pytest.mark.asyncio
    async def test_policy_rejects_high_even_if_llm_claims_low(self):
        from app.agent.policies import PolicyEngine
        from app.models import FixOperation, FixOperationType, FixProposal

        lying = FixProposal(
            root_cause="totally safe",
            operations=[
                FixOperation(operation=FixOperationType.DROP_INVALID_ROWS, column="order_id")
            ],
            risk=RiskLevel.LOW,  # LLM mislabels; policy re-classifies
        )
        p = PolicyEngine(approval_mode="auto")
        assert p.classify_fix(lying) == RiskLevel.HIGH
        ok, _ = p.can_deploy(lying, ApprovalStatus.AUTO_APPROVED)
        assert ok is False


class TestWarehouseUntouchedOnBlockedFixes:
    @pytest.mark.asyncio
    async def test_silent_corruption_blocked_before_any_write(self, env):
        from app.evaluation.adversarial import scenarios as adv

        sc = _scenario_by_id(adv(), "silent_corruption")
        state, ctx = await _run_with_ctx(sc, env)
        assert state.phase == Phase.SAFE_STOP
        assert state.deployment_status == DeploymentStatus.NOT_DEPLOYED
        failed = [c.name for c in state.validation_report.failed]
        assert any("expected_aggregate" in n or "aggregate" in n for n in failed)
        for table in ("clean.orders", "daily_revenue"):
            assert await ctx.store.warehouse.list_versions(table) == []

    @pytest.mark.asyncio
    async def test_mass_deletion_blocked_before_any_write(self, env):
        from app.evaluation.adversarial import scenarios as adv

        sc = _scenario_by_id(adv(), "massive_data_loss")
        state, ctx = await _run_with_ctx(sc, env)
        assert state.deployment_status == DeploymentStatus.NOT_DEPLOYED
        for table in ("clean.orders", "daily_revenue"):
            assert await ctx.store.warehouse.list_versions(table) == []


