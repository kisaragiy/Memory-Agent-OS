"""
Memory mutation intents — governed writes (not CRUD).

All mutations must flow: Control → Orchestrator → ExecutionEngine → MemoryLayer.apply_mutation
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


VALID_OPS = ("update_memory",)
VALID_TARGETS = ("semantic", "procedural", "world_state", "episodic")
VALID_ACTIONS = ("merge", "delete", "override", "inject", "rollback", "snapshot")


@dataclass
class MemoryMutationIntent:
    op: str = "update_memory"
    target: str = "semantic"
    action: str = "merge"
    fact: str = ""
    record_id: Optional[str] = None
    kind: str = "fact"
    snapshot_id: Optional[str] = None
    reason: str = ""
    actor: str = "system"
    inject_test: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryMutationIntent":
        return cls(
            op=str(data.get("op", "update_memory")),
            target=str(data.get("target", "semantic")),
            action=str(data.get("action", "merge")),
            fact=str(data.get("fact", "") or ""),
            record_id=data.get("record_id"),
            kind=str(data.get("kind", "fact")),
            snapshot_id=data.get("snapshot_id"),
            reason=str(data.get("reason", "") or ""),
            actor=str(data.get("actor", "system")),
            inject_test=bool(data.get("inject_test", False)),
        )


@dataclass
class MemoryMutationTrace:
    trace_id: str
    intent: Dict[str, Any]
    status: str
    result: Any = None
    error: Optional[str] = None
    sources: Dict[str, str] = field(default_factory=lambda: {
        "path": "kernel.execute_memory_op",
        "layer": "memory_layer.apply_mutation",
    })

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
