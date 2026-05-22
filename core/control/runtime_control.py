"""
Control Layer — BIOS / settings for Agent OS.

Separates user-facing output from developer diagnostics.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class RuntimeControl:
    USER = "user"
    DEVELOPER = "developer"
    DEBUG = "debug"

    VALID_MODES = (USER, DEVELOPER, DEBUG)

    def __init__(
        self,
        mode: str = USER,
        trace_enabled: Optional[bool] = None,
        log_level: str = "info",
    ):
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode: {mode}. Use one of {self.VALID_MODES}")
        self.mode = mode
        self.log_level = log_level
        if trace_enabled is None:
            trace_enabled = mode in (self.DEVELOPER, self.DEBUG)
        self.trace_enabled = trace_enabled

    def show_traceback(self) -> bool:
        return self.mode in (self.DEVELOPER, self.DEBUG)

    def show_trace(self) -> bool:
        return self.trace_enabled

    def format_error(self, error: Exception) -> Any:
        if self.mode == self.USER:
            return {"status": "error", "message": "任务执行失败，请稍后重试。"}
        return {
            "status": "error",
            "error": str(error),
            "mode": self.mode,
        }

    def format_execution_error(self, execution_result: Dict) -> Any:
        from core.control.output_policy import OutputPolicy

        if self.mode == self.USER:
            raw = execution_result.get("error") or ""
            return OutputPolicy.sanitize_error_message(self, str(raw))
        return execution_result

    def is_user_mode(self) -> bool:
        return self.mode == self.USER

    def allows_internal_fields(self) -> bool:
        return self.mode in (self.DEVELOPER, self.DEBUG)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "trace_enabled": self.trace_enabled,
            "log_level": self.log_level,
        }

    @classmethod
    def from_request(
        cls,
        *,
        mode: Optional[str] = None,
        developer: bool = False,
        trace: Optional[bool] = None,
    ) -> "RuntimeControl":
        resolved = mode or (cls.DEVELOPER if developer else cls.USER)
        return cls(mode=resolved, trace_enabled=trace)
