"""
Phase 4C — Policy & confirmation gate (no tool dispatch).
"""

from __future__ import annotations

import hashlib
from typing import List

from core.contracts.action_plan import ActionIntent, ActionPlan
from core.contracts.guard import GuardDecision

BLOCKED_TYPES = frozenset({"shell", "exec", "delete", "format", "sudo"})


class ActionGuard:
    @staticmethod
    def evaluate(
        action_plan: ActionPlan,
        *,
        confirmed: bool,
        agent_id: str = "local-agent",
        autonomous: bool = False,
        autonomy_meta: dict | None = None,
    ) -> GuardDecision:
        phase = "4D" if autonomous else "4C"
        meta = {
            "source": "action_guard",
            "phase": phase,
            "observable": True,
            "autonomy": autonomy_meta or {},
        }
        blocked: List[str] = []
        allowed_ids: List[str] = []
        risk_summary = {"low": 0, "medium": 0, "high": 0}

        if not action_plan.intents:
            return GuardDecision(
                approved=False,
                requires_confirmation=True,
                blocked_reasons=["empty_action_plan"],
                _meta={**meta, "fallback_reason": "empty_action_plan"},
            )

        for intent in action_plan.intents:
            risk_summary[intent.risk_level] = (
                risk_summary.get(intent.risk_level, 0) + 1
            )
            if intent.action_type in BLOCKED_TYPES:
                blocked.append(f"{intent.intent_id}:blocked_type:{intent.action_type}")
                continue
            if not intent.target_label and not intent.target_element_id:
                if intent.action_type in ("click", "focus", "type_text"):
                    blocked.append(f"{intent.intent_id}:missing_target")
                    continue
            allowed_ids.append(intent.intent_id)

        requires_confirmation = action_plan.requires_confirmation
        approved = bool(allowed_ids) and not blocked

        if requires_confirmation and not confirmed:
            return GuardDecision(
                approved=False,
                requires_confirmation=True,
                blocked_reasons=blocked or ["confirmation_required"],
                allowed_intent_ids=allowed_ids,
                risk_summary=risk_summary,
                _meta={**meta, "fallback_reason": "confirmation_required"},
            )

        if blocked and not allowed_ids:
            approved = False

        token = ""
        if approved and confirmed:
            token = ActionGuard._issue_token(agent_id, allowed_ids)

        if requires_confirmation:
            approved = approved and confirmed and bool(token)
        else:
            approved = approved and bool(allowed_ids)

        return GuardDecision(
            approved=approved,
            requires_confirmation=requires_confirmation,
            guard_token=token,
            blocked_reasons=blocked,
            allowed_intent_ids=allowed_ids,
            risk_summary=risk_summary,
            _meta=meta,
        )

    @staticmethod
    def _issue_token(agent_id: str, intent_ids: List[str]) -> str:
        payload = f"{agent_id}|{'|'.join(sorted(intent_ids))}"
        return hashlib.sha256(payload.encode()).hexdigest()[:24]

    @staticmethod
    def verify_token(token: str, agent_id: str, intent: ActionIntent) -> bool:
        expected = ActionGuard._issue_token(agent_id, [intent.intent_id])
        return token == expected

    @staticmethod
    def mark_intents_executable(
        action_plan: ActionPlan, decision: GuardDecision
    ) -> ActionPlan:
        allowed = set(decision.allowed_intent_ids)
        for intent in action_plan.intents:
            intent.execution_allowed = intent.intent_id in allowed
        action_plan.phase = "4D" if action_plan._meta.get("autonomous") else "4C"
        action_plan._meta["phase"] = action_plan.phase
        action_plan.mode = "guarded_execute"
        action_plan.execution_blocked_reason = ""
        action_plan._meta["guard_token"] = decision.guard_token
        return action_plan
