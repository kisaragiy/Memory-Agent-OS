"""
Presentation Policy — separates product output from developer diagnostics.

User mode: friendly status labels, no trace / traceback / raw execution blobs.
Developer/Debug: full result envelope + trace references.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from core.control.model_policy import ModelPolicy
from core.control.output_filter import OutputFilter
from core.control.runtime_control import RuntimeControl


# User-facing stream step labels (simplified for end users)
USER_STEP_LABELS: Dict[str, str] = {
    "started": "正在思考…",
    "input_normalized": "正在理解您的需求…",
    "schema_validated": "正在校验任务…",
    "plan_generated": "正在规划任务步骤…",
    "plan_built": "正在制定执行计划…",
    "tool_called": "正在调用系统能力…",
    "execution_result": "正在执行任务…",
    "execution_complete": "任务已完成",
    "memory_written": "正在更新记忆…",
    "observation_logged": "正在记录观察结果…",
    "desktop_observe": "正在刷新桌面画面…",
    "autonomous_step": "自主循环步骤完成",
    "error": "任务未能完成",
}


class PresentationPolicy:
    @staticmethod
    def user_step_label(step: str) -> str:
        return USER_STEP_LABELS.get(step, "正在处理…")

    @staticmethod
    def extract_display_text(raw: Any) -> str:
        if raw is None:
            return ""
        if isinstance(raw, str):
            return raw.strip()
        if isinstance(raw, dict):
            if isinstance(raw.get("message"), str) and raw.get("status") == "error":
                return raw["message"]
            if isinstance(raw.get("result"), str):
                return raw["result"].strip()
            inner = raw.get("result")
            if isinstance(inner, dict):
                for key in ("value", "stdout", "response", "narrative", "text"):
                    val = inner.get(key)
                    if val:
                        return str(val).strip()
            for key in ("response", "narrative", "display", "message"):
                val = raw.get(key)
                if isinstance(val, str) and val.strip():
                    return val.strip()
            if raw.get("status") == "error":
                from core.control.output_policy import OutputPolicy
                from core.control.runtime_control import RuntimeControl

                err = str(raw.get("error") or raw.get("message") or "")
                return OutputPolicy.sanitize_error_message(
                    RuntimeControl(mode=RuntimeControl.USER), err
                )
        return str(raw).strip()

    @classmethod
    def wrap_run_response(
        cls,
        control: RuntimeControl,
        raw: Any,
        *,
        session_id: str,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        display = cls.extract_display_text(raw)
        flags = ModelPolicy.resolve_flags(control.mode)
        base: Dict[str, Any] = {
            "session_id": session_id,
            "agent_id": session_id,
            "control": control.to_dict(),
        }

        if control.mode == RuntimeControl.USER:
            status = "success"
            if isinstance(raw, dict) and raw.get("status") == "error":
                status = "error"
            elif isinstance(raw, dict) and "error" in raw and not display:
                status = "error"
                display = "任务执行失败，请稍后重试。"
            return OutputFilter.filter_http_response(
                {
                    **base,
                    "mode": RuntimeControl.USER,
                    "status": status,
                    "display": display or "已完成。",
                },
                flags,
            )

        if control.mode == RuntimeControl.DEBUG:
            base["mode"] = RuntimeControl.DEBUG
        else:
            base["mode"] = RuntimeControl.DEVELOPER

        out: Dict[str, Any] = {
            **base,
            "status": "success",
            "display": display,
            "result": raw,
        }
        if trace_id and flags.show_trace:
            out["trace_id"] = trace_id
        return OutputFilter.filter_http_response(out, flags, trace_id=trace_id)

    @classmethod
    def sanitize_stream_event(
        cls, control: RuntimeControl, step: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        if control.mode == RuntimeControl.USER:
            if step == "execution_complete":
                display = cls.extract_display_text(data.get("result"))
                return {
                    "step": "display",
                    "data": {"label": USER_STEP_LABELS["execution_complete"], "text": display},
                }
            if step == "error":
                msg = "任务执行失败，请稍后重试。"
                if isinstance(data, dict) and data.get("message"):
                    msg = str(data["message"])
                return {"step": "display", "data": {"label": "任务未能完成", "text": msg}}
            return {
                "step": "status",
                "data": {"label": cls.user_step_label(step)},
            }

        flags = ModelPolicy.resolve_flags(control.mode)
        filtered = OutputFilter.filter_output(data, flags)
        return {"step": step, "data": filtered if isinstance(filtered, dict) else data}

    @classmethod
    def http_error_detail(cls, control: RuntimeControl, exc: Exception) -> Dict[str, Any]:
        if control.mode == RuntimeControl.USER:
            return {"status": "error", "message": "服务暂时不可用，请稍后重试。"}
        return {
            "status": "error",
            "error": str(exc),
            "mode": control.mode,
        }

    @classmethod
    def demo_response(cls, user_input: str, session_id: str) -> Dict[str, Any]:
        preview = (user_input or "示例任务")[:40]
        return {
            "mode": "demo",
            "status": "success",
            "display": f"【演示模式】已模拟完成：「{preview}」。正式环境将连接 Agent 内核执行。",
            "session_id": session_id,
            "agent_id": session_id,
            "control": {"mode": "user", "trace_enabled": False, "demo": True},
        }
