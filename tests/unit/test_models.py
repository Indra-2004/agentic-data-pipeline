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


