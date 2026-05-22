"""Per-session control settings (BIOS overrides) without forking runtimes."""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, Optional

from core.control.runtime_control import RuntimeControl


@dataclass
class SessionControl:
    mode: str = RuntimeControl.USER
    trace_enabled: Optional[bool] = None
    demo: bool = False

    def to_runtime_control(self) -> RuntimeControl:
        trace = self.trace_enabled
        if trace is None:
            trace = self.mode != RuntimeControl.USER
        return RuntimeControl(mode=self.mode, trace_enabled=trace)


class SessionControlRegistry:
    def __init__(self):
        self._lock = Lock()
        self._sessions: Dict[str, SessionControl] = {}

    def get(self, session_id: str) -> SessionControl:
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = SessionControl()
            return self._sessions[session_id]

    def set(
        self,
        session_id: str,
        *,
        mode: Optional[str] = None,
        trace_enabled: Optional[bool] = None,
        demo: Optional[bool] = None,
    ) -> SessionControl:
        sc = self.get(session_id)
        if mode is not None:
            if mode not in RuntimeControl.VALID_MODES:
                raise ValueError(f"Invalid mode: {mode}")
            sc.mode = mode
        if trace_enabled is not None:
            sc.trace_enabled = trace_enabled
        if demo is not None:
            sc.demo = demo
        return sc


SESSION_CONTROLS = SessionControlRegistry()
