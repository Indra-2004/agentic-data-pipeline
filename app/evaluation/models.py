"""Evaluation framework models.

A :class:`Scenario` describes a deterministic test input and its *expected*
behavior. The runner executes it through the real orchestrator and scores it
against the expectations. The headline metric is ``data_loss_rate`` (target 0):
the agent must prefer doing nothing over an unsafe data mutation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any




