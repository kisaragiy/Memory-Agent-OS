"""
Phase 4C/4D — Isolated UI action sandbox.

4C: dry-run simulation (default).
4D: live OS driver when GUARDED_UI_LIVE=1 + pyautogui available.
"""

from __future__ import annotations

import os
import uuid
from typing import Dict, List

from core.contracts.action_plan import ActionIntent
from core.contracts.guard import ExecutionReceipt
from core.os_automation.driver import OsAutomationDriver


class ExecutionSandbox:
    """In-process journal — not a second execution kernel."""

    _journal: List[Dict] = []

    @classmethod
    def reset_journal(cls) -> None:
        cls._journal = []

    @classmethod
    def get_journal(cls) -> List[Dict]:
        return list(cls._journal)

    @staticmethod
    def is_live_enabled() -> bool:
        return os.environ.get("GUARDED_UI_LIVE", "").strip() in ("1", "true", "yes")

    @classmethod
    def run(cls, intent: ActionIntent, *, dry_run: bool = True) -> ExecutionReceipt:
        live = cls.is_live_enabled() and not dry_run
        rollback_id = str(uuid.uuid4())[:10]

        if intent.action_type not in cls._allowed_types():
            return ExecutionReceipt(
                intent_id=intent.intent_id,
                action_type=intent.action_type,
                status="blocked",
                dry_run=dry_run,
                message=f"Action type not allowed: {intent.action_type}",
                rollback_id=rollback_id,
                _meta={"source": "sandbox", "observable": True},
            )

        if not live:
            msg = cls._simulate(intent)
            cls._journal.append(
                {
                    "rollback_id": rollback_id,
                    "intent": intent.to_dict(),
                    "simulated": True,
                    "reverted": False,
                }
            )
            return ExecutionReceipt(
                intent_id=intent.intent_id,
                action_type=intent.action_type,
                status="simulated",
                dry_run=True,
                message=msg,
                rollback_id=rollback_id,
                _meta={
                    "source": "sandbox_dry_run",
                    "live": False,
                    "observable": True,
                },
            )

        if not OsAutomationDriver.is_available():
            msg = cls._simulate(intent)
            return ExecutionReceipt(
                intent_id=intent.intent_id,
                action_type=intent.action_type,
                status="simulated",
                dry_run=True,
                message=msg + " [4D: pyautogui/display 不可用，已降级模拟]",
                rollback_id=rollback_id,
                _meta={
                    "source": "sandbox_live_fallback",
                    "fallback_reason": "pyautogui_unavailable",
                    "observable": True,
                },
            )

        try:
            msg, driver_meta = OsAutomationDriver.execute(intent)
            cls._journal.append(
                {
                    "rollback_id": rollback_id,
                    "intent": intent.to_dict(),
                    "simulated": False,
                    "reverted": False,
                    "driver_meta": driver_meta,
                }
            )
            return ExecutionReceipt(
                intent_id=intent.intent_id,
                action_type=intent.action_type,
                status="success",
                dry_run=False,
                message=msg,
                rollback_id=rollback_id,
                _meta={
                    "source": "sandbox_live_4d",
                    "live": True,
                    "observable": True,
                    **driver_meta,
                },
            )
        except Exception as exc:
            return ExecutionReceipt(
                intent_id=intent.intent_id,
                action_type=intent.action_type,
                status="error",
                dry_run=False,
                message=str(exc),
                rollback_id=rollback_id,
                _meta={
                    "source": "sandbox_live_error",
                    "fallback_reason": str(exc),
                    "observable": True,
                },
            )

    @classmethod
    def rollback_last(cls, count: int = 1) -> List[str]:
        reverted = []
        for entry in reversed(cls._journal[-count:]):
            if entry.get("reverted"):
                continue
            entry["reverted"] = True
            reverted.append(entry["rollback_id"])
        return reverted

    @staticmethod
    def _allowed_types():
        return frozenset({"click", "type_text", "focus", "scroll", "navigate"})

    @staticmethod
    def _simulate(intent: ActionIntent) -> str:
        label = intent.target_label or intent.target_element_id or "target"
        if intent.action_type == "click":
            return f"[dry-run] click「{label}」"
        if intent.action_type == "type_text":
            text = intent.parameters.get("text", "")
            return f"[dry-run] type「{text[:40]}」→ {label}"
        if intent.action_type == "focus":
            return f"[dry-run] focus「{label}」"
        if intent.action_type == "navigate":
            return f"[dry-run] navigate→「{label}」"
        if intent.action_type == "scroll":
            return f"[dry-run] scroll @「{label}」"
        return f"[dry-run] {intent.action_type}「{label}」"
