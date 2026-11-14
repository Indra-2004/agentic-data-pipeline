"""Rollback manager: deterministic, idempotent version restoration.

Rollback treats the warehouse as versioned (table, version) snapshots. Before
promotion the manager records ``active`` and ``candidate`` versions; on failure
or health decline it restores the previous active version and audits the event.

Deliberately idempotent: restoring the same version twice yields the same result,
and a rollback after an already-restored state is a no-op.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from app.storage.base import Warehouse


