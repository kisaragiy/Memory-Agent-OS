from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class MemoryRecordContract:
    id: str
    kind: str
    content: str
    importance: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReflectionRecord:
    should_retry: bool
    notes: List[str]
    failure_count: int
    step_count: int
    sources: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
