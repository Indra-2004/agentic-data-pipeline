"""Unit tests for the observability layer (metrics repository + health monitor)."""

from __future__ import annotations

import polars as pl
import pytest

from app.observability.metrics import MetricRepository
from app.observability.monitor import HealthMonitor
from app.storage import MemoryMetadataStore


