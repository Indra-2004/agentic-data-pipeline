"""Integration tests for the minimal FastAPI surface."""

from __future__ import annotations

import polars as pl
import pytest
from fastapi.testclient import TestClient

from app.config import settings


