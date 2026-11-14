"""Benchmark scenarios: 10 deterministic failures the agent must handle.

Each scenario's ``build`` function turns the healthy orders DataFrame into a
specific failure. Scenarios relying on baseline anomaly detection expose a
``seed_metrics`` async callback that the runner invokes to seed metric history
*before* the run.

Expected outcomes reflect the deterministic, conservative agent:
  - safe coercions (cast/parse/fill)   -> FIXED (auto-approve LOW risk)
  - uncertain/among benign changes     -> NO_ACTION (no destructive mutation)
  - destructive/needs-approval fixes   -> NO_ACTION or POLICY_REJECTED
"""

from __future__ import annotations

import random

import polars as pl

from app.evaluation.models import ExpectedOutcome, Scenario, ScenarioKind


def _R(seed: int) -> random.Random:
    return random.Random(seed)


def _healthy() -> pl.DataFrame:
    from app.data.loader import load_source

    return load_source("fixtures:orders.csv", "./datasets/fixtures")


