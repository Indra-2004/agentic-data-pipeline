"""Post-deployment health monitoring.

Formalizes the canary/monitor gate: after a candidate is staged and run through a
95/5 canary, the health monitor evaluates the canary-derived metrics against
thresholds. A breach means the promotion is unhealthy and triggers rollback.

Also provides a baseline comparison: the candidate snapshot is measured against
the pre-deployment metric history (anomaly detection) so the orchestration can
catch silent regressions that the canary split might not.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.data.anomaly import detect_anomalies


@dataclass
class HealthCheck:
    name: str
    passed: bool
    observed: Any = None
    threshold: Any = None
    message: str | None = None


@dataclass
class HealthReport:
    healthy: bool
    checks: list[HealthCheck] = field(default_factory=list)

    def failed_checks(self) -> list[HealthCheck]:
        return [c for c in self.checks if not c.passed]


