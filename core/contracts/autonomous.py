"""Phase 5 — Autonomous agent OS session contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AutonomousStepRecord:
    step_index: int
    phase: str
    status: str
    summary: str
    trace_id: str = ""
    intent_trace: Dict[str, Any] = field(default_factory=dict)
    _meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_index": self.step_index,
            "phase": self.phase,
            "status": self.status,
            "summary": self.summary,
            "trace_id": self.trace_id,
            "intent_trace": self.intent_trace,
            "_meta": dict(self._meta),
        }


@dataclass
class AutonomousSessionResult:
    session_id: str
    goal: str
    status: str
    steps: List[AutonomousStepRecord] = field(default_factory=list)
    final_output: Any = None
    _meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "goal": self.goal,
            "status": self.status,
            "steps": [s.to_dict() for s in self.steps],
            "final_output": self.final_output,
            "_meta": dict(self._meta),
        }
