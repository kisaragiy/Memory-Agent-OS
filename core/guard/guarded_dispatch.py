"""
Phase 4C — Map approved ActionPlan → kernel plan (tool syscalls only).
Not a router; produces data for ExecutionEngine path.
"""

from __future__ import annotations

from typing import Dict, List

from core.contracts.action_plan import ActionPlan
from core.contracts.guard import GuardDecision


class GuardedDispatch:
    @staticmethod
    def to_kernel_plan(
        action_plan: ActionPlan,
        decision: GuardDecision,
        *,
        dry_run: bool = True,
        agent_id: str = "local-agent",
    ) -> Dict:
        actions = []
        for intent in action_plan.intents:
            if not intent.execution_allowed:
                continue
            actions.append(
                {
                    "type": "tool",
                    "name": "guarded_ui_action",
                    "payload": {
                        "intent": intent.to_dict(),
                        "guard_token": decision.guard_token,
                        "dry_run": dry_run,
                        "agent_id": agent_id,
                    },
                }
            )

        return {
            "task": action_plan.user_goal,
            "task_type": "guarded_ui",
            "intent": "guarded_execute",
            "strategy": "4C_guarded_dispatch",
            "actions": actions,
            "_meta": {
                "source": "4C_guarded_dispatch",
                "dry_run": dry_run,
                "guard_token": decision.guard_token[:8] + "…",
                "intent_count": len(actions),
                "observable": True,
            },
        }

    @staticmethod
    def plan_to_syscalls(plan: Dict, trace_id: str) -> List[Dict]:
        syscalls = []
        for index, action in enumerate(plan.get("actions") or []):
            if action.get("type") != "tool":
                continue
            name = action.get("name")
            if name != "guarded_ui_action":
                continue
            syscalls.append(
                {
                    "type": name,
                    "payload": dict(action.get("payload") or {}),
                    "trace_id": f"{trace_id}:g{index}",
                }
            )
        return syscalls
