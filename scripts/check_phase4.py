#!/usr/bin/env python3
"""Phase 4 capability report — screen observation + OS automation (read-only check)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.contracts.action_plan import ActionIntent
from core.guard.execution_sandbox import ExecutionSandbox
from core.os_automation.driver import OsAutomationDriver
from core.platform.windows_desktop import WindowsDesktop


def main() -> int:
    print("=== Phase 4 — SYSTEM_BLUEPRINT compliance check ===\n")

    print("[4A] ScreenObserver (stub / env hint, no pyautogui)")
    from core.perception.screen_observer import ScreenObserver

    obs = ScreenObserver().observe("test")
    print(f"  captured={obs.captured} source={obs.source}")

    print("\n[4D] Windows desktop capture")
    print(f"  WSL: {WindowsDesktop.is_wsl()}  native_win: {WindowsDesktop.is_windows_native()}")
    print(f"  desktop_mode: {WindowsDesktop.desktop_mode_enabled()}")
    path, cap_meta = WindowsDesktop.capture_screenshot()
    print(f"  screenshot: {path or '(failed)'} meta={cap_meta.get('source')}")

    print("\n[4C/4D] ExecutionSandbox + OsAutomationDriver")
    print(f"  pyautogui available: {OsAutomationDriver.is_available()}")
    print(f"  GUARDED_UI_LIVE: {ExecutionSandbox.is_live_enabled()}")

    intent = ActionIntent(
        intent_id="probe",
        action_type="click",
        target_label="probe",
        risk_level="low",
    )
    dry = ExecutionSandbox.run(intent, dry_run=True)
    print(f"  dry-run: status={dry.status} msg={dry.message!r}")

    actions = ["click", "type_text", "focus", "scroll", "navigate"]
    print(f"  supported actions: {', '.join(actions)}")
    print("  mouse: click, focus, scroll | keyboard: type_text, hotkey(navigate=alt+tab)")

    if OsAutomationDriver.is_available() and os.environ.get("RUN_PHASE4_LIVE_PROBE") == "1":
        os.environ["GUARDED_UI_LIVE"] = "1"
        live = ExecutionSandbox.run(intent, dry_run=False)
        print(f"  live probe: status={live.status} meta={live._meta.get('source')}")
    else:
        print("  live probe: skipped (set RUN_PHASE4_LIVE_PROBE=1 to test real click)")

    print("\n[Path] guarded_ui_action → ExecutionSandbox → OsAutomationDriver (single ExecutionEngine)")
    print("OK — Phase 4 modules load.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
