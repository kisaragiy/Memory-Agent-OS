from __future__ import annotations

from threading import Lock
from typing import Dict, Optional

from core.runtime.agent_os_runtime import AgentOSRuntime
from core.control.runtime_control import RuntimeControl
from core.control.session_registry import SESSION_CONTROLS
from agent_service.settings import SETTINGS


class RuntimeManager:
    """One AgentOSRuntime per agent_id (single kernel per session)."""

    def __init__(self):
        self._lock = Lock()
        self._runtimes: Dict[str, AgentOSRuntime] = {}

    def _base_control(self, session_id: str) -> RuntimeControl:
        sc = SESSION_CONTROLS.get(session_id)
        if sc.mode != RuntimeControl.USER or sc.trace_enabled is not None:
            return sc.to_runtime_control()
        return RuntimeControl(
            mode=SETTINGS.control_mode,
            trace_enabled=SETTINGS.control_mode != RuntimeControl.USER,
        )

    def get(
        self,
        agent_id: str | None = None,
        *,
        mode: Optional[str] = None,
        developer: bool = False,
        trace: Optional[bool] = None,
    ) -> AgentOSRuntime:
        aid = agent_id or SETTINGS.default_agent_id

        if mode or developer or trace is not None:
            SESSION_CONTROLS.set(
                aid,
                mode=mode or (RuntimeControl.DEVELOPER if developer else None),
                trace_enabled=trace,
            )

        control = self._base_control(aid)
        if mode:
            control = RuntimeControl.from_request(mode=mode, trace=trace)
        elif developer:
            control = RuntimeControl.from_request(developer=True, trace=trace)

        with self._lock:
            rt = self._runtimes.get(aid)
            if rt is None:
                rt = AgentOSRuntime(
                    agent_id=aid,
                    control=control,
                    observe_screen=(
                        SETTINGS.enable_autonomous or SETTINGS.enable_windows_desktop
                    ),
                    plan_actions=SETTINGS.enable_autonomous
                    or SETTINGS.enable_windows_desktop,
                    autonomous=SETTINGS.enable_autonomous,
                    dry_run=not SETTINGS.enable_live,
                )
                self._runtimes[aid] = rt
            else:
                rt.set_mode(control.mode)
                rt.control.trace_enabled = control.trace_enabled
            return rt

    def control_for(self, agent_id: str) -> RuntimeControl:
        return self.get(agent_id).control

    def invalidate(self, agent_id: str) -> None:
        with self._lock:
            self._runtimes.pop(agent_id, None)


RUNTIME_MANAGER = RuntimeManager()
