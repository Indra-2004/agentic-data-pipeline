"""Unit tests for Phase 1: config settings and Pydantic domain models."""

from __future__ import annotations

from app.config import ApprovalMode, LLMProviderKind, Settings, StorageBackend
from app.models import (
    DataType,
    DriftEvent,
    DriftEventType,
    FixOperation,
    FixOperationType,
    FixProposal,
    OnError,
    Phase,
    Pipeline,
    PipelineStage,
    PipelineTriageState,
    RiskLevel,
    SchemaDefinition,
    Severity,
    ValidationCheck,
    ValidationReport,
    ValidationStatus,
    ColumnDefinition,
)


def _orders_schema(version: int = 3) -> SchemaDefinition:
    return SchemaDefinition(
        table="orders",
        version=version,
        columns=[
            ColumnDefinition(name="order_id", type=DataType.INTEGER),
            ColumnDefinition(name="amount", type=DataType.DOUBLE),
            ColumnDefinition(name="currency", type=DataType.VARCHAR),
        ],
    )


class TestSettings:
    def test_defaults(self):
        s = Settings(_env_file=None)
        assert s.llm_provider == LLMProviderKind.DETERMINISTIC
        assert s.approval_mode == ApprovalMode.AUTO
        assert s.storage_backend == StorageBackend.SQLITE
        assert s.max_iterations > 0
        assert s.max_tool_calls > 0

    def test_env_prefix_override(self, monkeypatch):
        monkeypatch.setenv("SHP_LLM_PROVIDER", "openai")
        monkeypatch.setenv("SHP_APPROVAL_MODE", "manual")
        s = Settings(_env_file=None)
        assert s.llm_provider == LLMProviderKind.OPENAI
        assert s.approval_mode == ApprovalMode.MANUAL


