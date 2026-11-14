"""Reproducible fixture generator for the demo pipelines.

Run: python datasets/fixtures/_generate.py

Writes healthy baseline sources:
  - orders.csv      : 600 orders, numeric amount, valid customer refs
  - customers.csv   : 200 customers

The drifted/scenario variants are generated at runtime by
``app/evaluation/scenarios.py`` (Phase 7) from these fixtures.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import polars as pl

CURRENCIES = ["USD", "EUR", "GBP", "JPY"]
STATUS = ["completed", "pending", "cancelled", "shipped"]


def gen_customers(rng: random.Random, n: int = 200) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "customer_id": list(range(1, n + 1)),
            "tier": [rng.choice(["standard", "gold", "platinum"]) for _ in range(n)],
            "country": [rng.choice(["US", "DE", "FR", "UK", "JP"]) for _ in range(n)],
        }
    )


