"""
Alignment — batch capability and output visibility flags.

Resolved only via ModelPolicy.resolve_flags; consumed by OutputFilter + ExecutionGate.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any, Dict


@dataclass(frozen=True)
class AlignmentFlags:
    # Output visibility (batch)
    show_reasoning: bool = False
    show_trace: bool = False
    show_memory: bool = False
    show_tool_io: bool = False
    show_system_meta: bool = False

    # Capability gates (batch)
    enable_code_execution: bool = True
    enable_llm_reasoning: bool = False
    enable_narrative: bool = True
    enable_vision: bool = False
    enable_memory_write: bool = True
    enable_autonomy: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any] | None) -> "AlignmentFlags":
        if not data:
            return cls()
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        return cls(**{k: bool(v) for k, v in data.items() if k in known})

    def merge(self, **overrides: Any) -> "AlignmentFlags":
        known = {f.name for f in self.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        clean = {k: v for k, v in overrides.items() if k in known}
        return replace(self, **clean)


@dataclass
class AlignmentSpec:
    """Resolved alignment envelope for a single kernel turn."""

    control_mode: str
    flags: AlignmentFlags

    def to_dict(self) -> Dict[str, Any]:
        return {"control_mode": self.control_mode, "flags": self.flags.to_dict()}
