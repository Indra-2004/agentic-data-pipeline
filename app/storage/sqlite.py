"""SQLite storage backend.

Implements both :class:`MetadataStore` and :class:`Warehouse` on top of a single
SQLite database file (SQLAlchemy ORM for metadata, Parquet blobs for versioned
warehouse datasets). Warehouse rows are stored as lossless Parquet blobs so
Polars dtypes survive the round trip, giving deterministic snapshot/restore
behaviour for canary and rollback.

DuckDB/Postgres adapters can replace this class later without touching callers.
"""

from __future__ import annotations

import io
import json
from typing import Any

import polars as pl
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    LargeBinary,
    Text,
    create_engine,
    select,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.models import Pipeline, PipelineTriageState
from app.models.quality import QualityReport
from app.models.schema import DriftEvent, SchemaDefinition
from app.storage.base import MetadataStore, Warehouse


class Base(DeclarativeBase):
    pass


class AgentStateRow(Base):
    __tablename__ = "agent_state"
    run_id = Column(String, primary_key=True)
    state_json = Column(Text)


class PipelineRow(Base):
    __tablename__ = "pipelines"
    id = Column(String, primary_key=True)
    pipeline_json = Column(Text)


class SchemaRow(Base):
    __tablename__ = "schema_registry"
    table = Column(String, primary_key=True)
    version = Column(Integer, primary_key=True)
    schema_json = Column(Text)


class RunRow(Base):
    __tablename__ = "pipeline_runs"
    run_id = Column(String, primary_key=True)
    pipeline_id = Column(String)
    status = Column(String)
    issues_json = Column(Text, default="[]")
    quality_json = Column(Text, nullable=True)


class MetricRow(Base):
    __tablename__ = "metric_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    table = Column(String, index=True)
    timestamp = Column(String)
    name = Column(String)
    value = Column(Float)


