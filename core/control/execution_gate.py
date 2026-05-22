"""
Execution Gate — last line before syscalls; blocks NL / wrong tools.
"""

from __future__ import annotations

from typing import Dict, List

from core.contracts.intent import ExecutionChannel, IntentRoute, IntentType
from core.control.alignment_spec import AlignmentFlags
from core.control.intent_router import IntentRouter


class ExecutionIsolationError(Exception):
    """Raised when a plan violates execution isolation policy."""


ALLOWED_TOOLS: Dict[IntentType, frozenset] = {
    IntentType.CHAT: frozenset({"narrative_respond"}),
    IntentType.NARRATIVE: frozenset({"narrative_respond"}),
    IntentType.CODE: frozenset({"execute_code", "narrative_respond"}),
    IntentType.MEMORY: frozenset(),
    IntentType.UI: frozenset({"guarded_ui_action", "narrative_respond"}),
    IntentType.UNKNOWN: frozenset({"narrative_respond"}),
}


class ExecutionGate:
    @classmethod
    def enforce_plan(
        cls,
        plan: Dict,
        route: IntentRoute,
        flags: AlignmentFlags | None = None,
    ) -> Dict:
        allowed = ALLOWED_TOOLS.get(route.intent, frozenset({"narrative_respond"}))
        clean: List[Dict] = []
        violations: List[str] = []

        for action in plan.get("actions") or []:
            if action.get("type") != "tool":
                continue
            name = action.get("name") or ""
            payload = dict(action.get("payload") or {})

            if flags and not flags.enable_code_execution and name == "execute_code":
                violations.append("code_execution_disabled_by_alignment")
                continue
            if flags and not flags.enable_narrative and name == "narrative_respond":
                violations.append("narrative_disabled_by_alignment")
                continue

            if name == "execute_code":
                if not route.allow_execute_code:
                    violations.append("execute_code_blocked_by_intent")
                    continue
                code = str(payload.get("code") or "")
                if IntentRouter.looks_like_natural_language(code):
                    violations.append("natural_language_in_execute_code")
                    continue
                if not IntentRouter.is_safe_python_snippet(code):
                    violations.append("unsafe_python_snippet")
                    continue

            if name and name not in allowed and name != "guarded_ui_action":
                violations.append(f"tool_not_allowed:{name}")
                continue

            clean.append(action)

        meta = dict(plan.get("_meta") or {})
        meta["execution_gate"] = {
            "violations": violations,
            "allowed_tools": sorted(allowed),
            "intent": route.intent.value,
        }

        if not clean:
            clean = cls._fallback_narrative_action(plan.get("task") or "")

        return {**plan, "actions": clean, "_meta": meta}

    @staticmethod
    def _fallback_narrative_action(task: str) -> List[Dict]:
        return [
            {
                "type": "tool",
                "name": "narrative_respond",
                "payload": {"prompt": task},
            }
        ]

    @classmethod
    def filter_syscalls(
        cls,
        syscalls: List[Dict],
        route: IntentRoute,
        flags: AlignmentFlags | None = None,
    ) -> List[Dict]:
        out: List[Dict] = []
        for sc in syscalls:
            tool = sc.get("type")
            if flags and not flags.enable_code_execution and tool == "execute_code":
                continue
            if flags and not flags.enable_narrative and tool == "narrative_respond":
                continue
            if tool == "execute_code" and not route.allow_execute_code:
                continue
            if tool == "execute_code":
                code = (sc.get("payload") or {}).get("code", "")
                if IntentRouter.looks_like_natural_language(code):
                    continue
            out.append(sc)
        return out
