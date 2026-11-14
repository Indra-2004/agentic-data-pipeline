"""Storage package: protocols, SQLite + in-memory backends, and a factory."""

from __future__ import annotations

from pathlib import Path

from app.storage.base import BackendStore, MetadataStore, Warehouse
from app.storage.memory import MemoryMetadataStore, MemoryWarehouse
from app.storage.sqlite import SQLiteMetadataStore, SQLiteWarehouse


