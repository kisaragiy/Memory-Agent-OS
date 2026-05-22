from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class MemoryKind(str, Enum):
    FACT = "fact"
    PREFERENCE = "preference"
    EPISODE = "episode"
    PROCEDURAL = "procedural"
    PROJECT = "project"
    CONVERSATION = "conversation"


@dataclass
class MemoryRecord:
    id: str
    agent_id: str
    kind: MemoryKind
    content: str
    importance: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @staticmethod
    def create(
        agent_id: str,
        kind: MemoryKind,
        content: str,
        importance: float = 0.5,
        metadata: Optional[Dict] = None,
    ) -> "MemoryRecord":
        return MemoryRecord(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            kind=kind,
            content=content.strip(),
            importance=importance,
            metadata=metadata or {},
        )


@dataclass
class ConversationTurn:
    role: str
    content: str
    trace_id: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class Episode:
    trace_id: str
    user_input: str
    plan_summary: str
    status: str
    assistant_output: str = ""
    result: Any = None
    reflection: Optional[Dict] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
