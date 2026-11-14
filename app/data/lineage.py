"""Data lineage graph and blast-radius computation.

Builds a lightweight DAG of ``node -> node`` edges carrying the columns that
flow between them. Given a set of changed columns, computes the downstream
blast radius (which stages/tables may be affected).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LineageEdge:
    source: str
    destination: str
    columns: list[str] = field(default_factory=list)


