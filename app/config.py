"""Application configuration via pydantic-settings.

Every tunable is read from environment variables (prefix ``SHP_``) or an
optional ``.env`` file. This keeps provider choice, agent guardrails, approval
mode and storage backend declarative and environment-driven.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProviderKind(str, Enum):
    DETERMINISTIC = "deterministic"
    OPENAI = "openai"


class ApprovalMode(str, Enum):
    AUTO = "auto"              # LOW auto-stages; unsupported/HIGH rejected without gate
    MANUAL = "manual"          # MEDIUM/HIGH require explicit approval (harness supplies it)
    HUMAN_IN_LOOP = "human_in_loop"  # MEDIUM/HIGH pause for a real human


