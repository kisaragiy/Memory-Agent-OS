from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List


@dataclass
class NarrativeState:
    theme: str = ""
    tension: float = 0.0
    conflicts: List[str] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    user_focus: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NarrativeState":
        return cls(
            theme=data.get("theme", ""),
            tension=float(data.get("tension", 0)),
            conflicts=list(data.get("conflicts") or []),
            events=list(data.get("events") or []),
            user_focus=data.get("user_focus", ""),
        )
