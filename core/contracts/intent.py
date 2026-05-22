"""Intent classification contracts — deterministic routing before execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class IntentType(str, Enum):
    CHAT = "chat"
    NARRATIVE = "narrative"
    CODE = "code"
    MEMORY = "memory"
    UI = "ui"
    UNKNOWN = "unknown"


class ExecutionChannel(str, Enum):
    """Where work is handled — never mix NL with execute_code."""

    NARRATIVE = "narrative"
    PLANNER = "planner"
    MEMORY = "memory"
    GUARD = "guard"
    NONE = "none"


@dataclass
class IntentRoute:
    intent: IntentType
    channel: ExecutionChannel
    allow_execute_code: bool = False
    confidence: float = 1.0
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent.value,
            "channel": self.channel.value,
            "allow_execute_code": self.allow_execute_code,
            "confidence": self.confidence,
            "reasons": self.reasons,
        }


@dataclass
class IntentClassification:
    route: IntentRoute
    normalized_task: str
    blocked_from_execution: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "route": self.route.to_dict(),
            "normalized_task": self.normalized_task,
            "blocked_from_execution": self.blocked_from_execution,
        }
