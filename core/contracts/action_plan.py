"""
Phase 4B — Action plan contracts (intents only, no execution).
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List
import uuid


@dataclass
class ActionIntent:
    intent_id: str
    action_type: str
    target_element_id: str = ""
    target_label: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    risk_level: str = "medium"
    execution_allowed: bool = False
    rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def create(
        cls,
        action_type: str,
        target_label: str = "",
        target_element_id: str = "",
        **kwargs,
    ) -> "ActionIntent":
        return cls(
            intent_id=str(uuid.uuid4())[:8],
            action_type=action_type,
            target_element_id=target_element_id,
            target_label=target_label,
            **kwargs,
        )


@dataclass
class ActionPlan:
    """Proposed OS/UI actions — not dispatched until Phase 4C."""

    phase: str = "4B"
    mode: str = "plan_only"
    user_goal: str = ""
    intents: List[ActionIntent] = field(default_factory=list)
    requires_confirmation: bool = True
    execution_blocked_reason: str = "Phase 4B: planning only; execution gated for 4C"
    constraints: List[str] = field(default_factory=list)
    _meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase,
            "mode": self.mode,
            "user_goal": self.user_goal,
            "intents": [i.to_dict() for i in self.intents],
            "requires_confirmation": self.requires_confirmation,
            "execution_blocked_reason": self.execution_blocked_reason,
            "constraints": list(self.constraints),
            "_meta": dict(self._meta),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActionPlan":
        intents = []
        for item in data.get("intents") or []:
            intents.append(
                ActionIntent(
                    intent_id=item.get("intent_id", str(uuid.uuid4())[:8]),
                    action_type=item.get("action_type", "unknown"),
                    target_element_id=item.get("target_element_id", ""),
                    target_label=item.get("target_label", ""),
                    parameters=dict(item.get("parameters") or {}),
                    risk_level=item.get("risk_level", "medium"),
                    execution_allowed=bool(item.get("execution_allowed", False)),
                    rationale=item.get("rationale", ""),
                )
            )
        return cls(
            phase=data.get("phase", "4B"),
            mode=data.get("mode", "plan_only"),
            user_goal=data.get("user_goal", ""),
            intents=intents,
            requires_confirmation=data.get("requires_confirmation", True),
            execution_blocked_reason=data.get(
                "execution_blocked_reason", ""
            ),
            constraints=list(data.get("constraints") or []),
            _meta=dict(data.get("_meta") or {}),
        )
