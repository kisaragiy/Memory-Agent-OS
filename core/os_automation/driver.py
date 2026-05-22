"""
Phase 4D — OS automation driver.

ONLY invoked from ExecutionSandbox (via guarded_ui_action → ExecutionEngine).
Not a second kernel. Requires pyautogui + display (typically Windows host).
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Tuple

from core.contracts.action_plan import ActionIntent
from core.platform.windows_desktop import WindowsDesktop


class OsAutomationDriver:
    @staticmethod
    def is_available() -> bool:
        if os.environ.get("AUTONOMOUS_DISABLE_DRIVER", "").strip() in ("1", "true"):
            return False
        if WindowsDesktop.automation_available():
            return True
        try:
            import pyautogui  # noqa: F401

            return True
        except ImportError:
            return False

    @staticmethod
    def execute(intent: ActionIntent) -> Tuple[str, Dict[str, Any]]:
        meta: Dict[str, Any] = {
            "source": "os_automation_driver",
            "phase": "4D",
            "observable": True,
        }
        if not OsAutomationDriver.is_available():
            meta["fallback_reason"] = "pyautogui_unavailable"
            return (
                f"[4D blocked] pyautogui 不可用；请 pip install pyautogui 并在有桌面的环境运行",
                meta,
            )

        if WindowsDesktop.is_wsl() or (
            WindowsDesktop.is_windows_native() and not WindowsDesktop._pyautogui_ok()
        ):
            return WindowsDesktop.execute_intent(intent)

        import pyautogui

        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = float(os.environ.get("PYAUTOGUI_PAUSE", "0.25"))

        pre_pos = pyautogui.position()
        meta["pre_position"] = {"x": pre_pos.x, "y": pre_pos.y}

        try:
            msg = OsAutomationDriver._dispatch(pyautogui, intent, meta)
            post_pos = pyautogui.position()
            meta["post_position"] = {"x": post_pos.x, "y": post_pos.y}
            meta["live"] = True
            return msg, meta
        except Exception as exc:
            meta["error"] = str(exc)
            meta["fallback_reason"] = "driver_exception"
            raise

    @staticmethod
    def _dispatch(pyautogui, intent: ActionIntent, meta: dict) -> str:
        label = intent.target_label or intent.target_element_id
        bounds = intent.parameters.get("bounds") if intent.parameters else None

        if intent.action_type == "click":
            x, y = OsAutomationDriver._resolve_point(bounds, pyautogui)
            pyautogui.click(x, y)
            meta["coordinates"] = {"x": x, "y": y}
            return f"[live] click「{label}」@({x},{y})"

        if intent.action_type == "type_text":
            text = str(intent.parameters.get("text", ""))
            if bounds:
                x, y = OsAutomationDriver._resolve_point(bounds, pyautogui)
                pyautogui.click(x, y)
                time.sleep(0.1)
            pyautogui.write(text, interval=0.02)
            return f"[live] type「{text[:40]}」→ {label}"

        if intent.action_type == "focus":
            x, y = OsAutomationDriver._resolve_point(bounds, pyautogui)
            pyautogui.click(x, y)
            return f"[live] focus「{label}」@({x},{y})"

        if intent.action_type == "scroll":
            clicks = int(intent.parameters.get("clicks", -3))
            pyautogui.scroll(clicks)
            return f"[live] scroll {clicks} @「{label}」"

        if intent.action_type == "navigate":
            pyautogui.hotkey("alt", "tab")
            return f"[live] navigate (alt+tab) →「{label}」"

        raise ValueError(f"Unsupported live action: {intent.action_type}")

    @staticmethod
    def _resolve_point(bounds, pyautogui) -> Tuple[int, int]:
        if isinstance(bounds, dict):
            x = bounds.get("x")
            y = bounds.get("y")
            w = bounds.get("w", bounds.get("width", 0))
            h = bounds.get("h", bounds.get("height", 0))
            if x is not None and y is not None:
                return int(x) + int(w) // 2, int(y) + int(h) // 2
        size = pyautogui.size()
        return size.width // 2, size.height // 2
