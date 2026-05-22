"""
Phase 4C — Guard & execution receipts (no dispatch logic here).
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List


@dataclass
class GuardDecision:
    approved: bool
    requires_confirmation: bool
    guard_token: str = ""
    blocked_reasons: List[str] = field(default_factory=list)
    allowed_intent_ids: List[str] = field(default_factory=list)
    risk_summary: Dict[str, int] = field(default_factory=dict)
    _meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExecutionReceipt:
    intent_id: str
    action_type: str
    status: str
    dry_run: bool
    message: str
    rollback_id: str = ""
    _meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GuardedExecutionResult:
    phase: str = "4C"
    mode: str = "guarded"
    receipts: List[ExecutionReceipt] = field(default_factory=list)
    rollback_available: bool = False
    _meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase,
            "mode": self.mode,
            "receipts": [r.to_dict() for r in self.receipts],
            "rollback_available": self.rollback_available,
            "_meta": dict(self._meta),
        }
