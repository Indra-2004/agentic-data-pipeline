"""Tool abstraction.

Each tool is a strongly-typed callable returning structured output (dicts or
Pydantic models). Tools are gated by the :class:`PolicyEngine` *before* dispatch;
an agent/LLM cannot invoke a tool that the policy doesn't permit for the current
phase.
"""

from __future__ import annotations

import types
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, replace
from typing import Any

from app.agent.policies import ActionClass

ToolHandler = Callable[..., Awaitable[Any]]


