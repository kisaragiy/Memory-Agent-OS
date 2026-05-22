"""
Phase 4C — Guarded UI action tool (sole syscall path for UI execution).

Invoked ONLY via ExecutionEngine → ToolRouter.
"""

from __future__ import annotations

from typing import Dict

from core.contracts.action_plan import ActionIntent
from core.guard.action_guard import ActionGuard
from core.guard.execution_sandbox import ExecutionSandbox


class GuardedUiActionTool:
    def execute(self, payload: Dict) -> Dict:
        try:
            intent_data = payload.get("intent")
            if not intent_data:
                return {
                    "status": "error",
                    "result": None,
                    "error": "Missing intent in payload",
                    "_meta": {"source": "guarded_ui_action", "observable": True},
                }

            intent = ActionIntent(
                intent_id=intent_data.get("intent_id", ""),
                action_type=intent_data.get("action_type", ""),
                target_element_id=intent_data.get("target_element_id", ""),
                target_label=intent_data.get("target_label", ""),
                parameters=dict(intent_data.get("parameters") or {}),
                risk_level=intent_data.get("risk_level", "medium"),
                execution_allowed=bool(intent_data.get("execution_allowed")),
                rationale=intent_data.get("rationale", ""),
            )

            token = payload.get("guard_token", "")
            agent_id = payload.get("agent_id", "local-agent")
            if not ActionGuard.verify_token(token, agent_id, intent):
                return {
                    "status": "error",
                    "result": None,
                    "error": "Invalid or expired guard_token",
                    "_meta": {"source": "guarded_ui_action", "observable": True},
                }

            if not intent.execution_allowed:
                return {
                    "status": "error",
                    "result": None,
                    "error": "Intent not approved for execution",
                    "_meta": {"source": "guarded_ui_action", "observable": True},
                }

            dry_run = bool(payload.get("dry_run", True))
            receipt = ExecutionSandbox.run(intent, dry_run=dry_run)

            return {
                "status": "success" if receipt.status in ("success", "simulated") else "error",
                "result": {
                    "value": receipt.message,
                    "stdout": receipt.message,
                    "receipt": receipt.to_dict(),
                    "locals": {},
                },
                "error": None if receipt.status != "blocked" else receipt.message,
                "_meta": receipt._meta,
            }
        except Exception as e:
            return {
                "status": "error",
                "result": None,
                "error": str(e),
                "_meta": {"source": "guarded_ui_action_error", "observable": True},
            }
