"""Evaluation framework tests: hard gates on agent behavior.

The headline gate is data loss: it must be zero in every scenario, including the
adversarial safety attacks. The agent must prefer doing nothing over an unsafe
data modification.
"""

from __future__ import annotations

import pytest

from app.evaluation import metrics as metrics_mod
from app.evaluation.adversarial import scenarios as adversarial_scenarios
from app.evaluation.metrics import compute_metrics
from app.evaluation.runner import run_all
from app.evaluation.scenarios import scenarios as benchmark_scenarios


@pytest.mark.asyncio
async def test_scenario_inventory():
    assert len(benchmark_scenarios()) == 10
    assert len(adversarial_scenarios()) == 5
    ids = [s.id for s in benchmark_scenarios() + adversarial_scenarios()]
    assert len(ids) == len(set(ids)), "scenario ids must be unique"


