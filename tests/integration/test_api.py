"""Integration tests for the minimal FastAPI surface."""

from __future__ import annotations

import polars as pl
import pytest
from fastapi.testclient import TestClient

from app.config import settings


@pytest.fixture()
def client(monkeypatch, tmp_path):
    from app.config import StorageBackend

    monkeypatch.setattr(settings, "storage_backend", StorageBackend.MEMORY)
    monkeypatch.setattr(settings, "db_path", tmp_path / "api.db")
    from app.api.app import create_app

    with TestClient(create_app()) as c:
        yield c


class TestHealth:
    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert body["llm_provider"] == "deterministic"
        assert body["storage_backend"] == "memory"


class TestPipelines:
    def test_list_pipelines(self, client):
        r = client.get("/pipelines")
        assert r.status_code == 200
        pipelines = r.json()
        assert any(p["id"] == "orders" for p in pipelines)
        orders = next(p for p in pipelines if p["id"] == "orders")
        assert "orders_clean" in orders["stages"]


