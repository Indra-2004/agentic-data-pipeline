"""Diagnosis engine: turn deterministic evidence into ranked hypotheses.

Hybrid approach: rule-based hypotheses are built from the drift events and
quality anomalies the system measured deterministically. The LLM then refines a
root-cause description and a fix proposal. The *selection* of a hypothesis is
still deterministic — the agent never lets the model pick a diagnosis blindly.
"""

from __future__ import annotations

import uuid

from app.models import (
    DriftEvent,
    DriftEventType,
    Hypothesis,
    QualityAnomaly,
)


