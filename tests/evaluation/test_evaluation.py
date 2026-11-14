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


