from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class UIElement:
    element_id: str
    role: str
    label: str
    bounds: Optional[Dict[str, int]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ObservationState:
    """Phase 4A — observation only, no actions."""

    mode: str = "observation_only"
    captured: bool = False
    source: str = "none"
    elements: List[UIElement] = field(default_factory=list)
    raw_hint: str = ""
    constraints: List[str] = field(default_factory=list)
    _meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "captured": self.captured,
            "source": self.source,
            "elements": [e.to_dict() for e in self.elements],
            "raw_hint": self.raw_hint,
            "constraints": list(self.constraints),
            "_meta": dict(self._meta),
        }
