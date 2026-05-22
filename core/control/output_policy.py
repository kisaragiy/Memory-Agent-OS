"""
Output Policy — strict user vs developer isolation for execution artifacts.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

from core.control.runtime_control import RuntimeControl

_PYTHON_ERROR = re.compile(
    r"name\s+'.+'\s+is\s+not\s+defined|SyntaxError|Traceback|File \"",
    re.IGNORECASE,
)


class OutputPolicy:
    @staticmethod
    def sanitize_execution_step(
        control: RuntimeControl, step_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        if control.allows_internal_fields():
            return step_result
        out = dict(step_result)
        if out.get("status") != "success":
            out["error"] = "任务执行失败，请稍后重试。"
            if isinstance(out.get("result"), dict):
                out["result"] = None
        return out

    @staticmethod
    def sanitize_error_message(control: RuntimeControl, message: str) -> str:
        if control.allows_internal_fields():
            return message
        if _PYTHON_ERROR.search(message or ""):
            return "任务执行失败，请稍后重试。"
        return "任务未能完成，请稍后重试。"

    @staticmethod
    def attach_intent_meta(
        payload: Dict[str, Any],
        *,
        intent: Optional[str],
        channel: Optional[str],
    ) -> Dict[str, Any]:
        meta = dict(payload.get("_meta") or {})
        meta["intent"] = intent
        meta["channel"] = channel
        payload["_meta"] = meta
        return payload
