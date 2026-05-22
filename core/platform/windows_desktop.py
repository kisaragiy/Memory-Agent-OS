"""
Windows desktop bridge — capture + input for Agent OS Phase 4.

- Native Windows Python: pyautogui when available.
- WSL: PowerShell captures/clicks the **host Windows** desktop (not Linux framebuffer).

Single entry for VisionObserver + OsAutomationDriver extensions.
"""

from __future__ import annotations

import os
import platform
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from core.contracts.action_plan import ActionIntent


def _env_true(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes")


class WindowsDesktop:
    @staticmethod
    def is_wsl() -> bool:
        if platform.system() != "Linux":
            return False
        try:
            with open("/proc/version", encoding="utf-8", errors="ignore") as f:
                return "microsoft" in f.read().lower()
        except OSError:
            return False

    @staticmethod
    def is_windows_native() -> bool:
        return platform.system() == "Windows"

    @classmethod
    def desktop_mode_enabled(cls) -> bool:
        if _env_true("AGENT_WINDOWS_DESKTOP"):
            return True
        if cls.is_windows_native():
            return _env_true("AUTONOMOUS_CAPTURE") or _env_true("USE_VISION_OBSERVER")
        if cls.is_wsl():
            return _env_true("AUTONOMOUS_CAPTURE") or _env_true("AGENT_WINDOWS_DESKTOP")
        return False

    @classmethod
    def capture_enabled(cls) -> bool:
        if os.environ.get("SCREENSHOT_PATH", "").strip():
            return True
        if _env_true("AUTONOMOUS_CAPTURE"):
            return True
        return cls.desktop_mode_enabled()

    @classmethod
    def automation_available(cls) -> bool:
        if _env_true("AUTONOMOUS_DISABLE_DRIVER"):
            return False
        if cls._pyautogui_ok():
            return True
        return cls.is_wsl() or cls.is_windows_native()

    @classmethod
    def default_screenshot_path(cls) -> Path:
        env = os.environ.get("SCREENSHOT_PATH", "").strip()
        if env:
            return Path(env)
        if cls.is_wsl():
            public = Path("/mnt/c/Users/Public/memory_chat_screen.png")
            if public.parent.exists():
                return public
        return Path(tempfile.gettempdir()) / "memory_chat_screen.png"

    @classmethod
    def capture_screenshot(
        cls, out_path: Optional[Path] = None
    ) -> Tuple[Optional[str], Dict[str, Any]]:
        meta: Dict[str, Any] = {"observable": True, "phase": "4D"}
        out = Path(out_path) if out_path else cls.default_screenshot_path()

        if cls._pyautogui_ok():
            try:
                import pyautogui

                shot = pyautogui.screenshot()
                out.parent.mkdir(parents=True, exist_ok=True)
                shot.save(out)
                meta["source"] = "pyautogui"
                meta["path"] = str(out)
                return str(out), meta
            except Exception as exc:
                meta["pyautogui_error"] = str(exc)

        if cls.is_wsl() or cls.is_windows_native():
            path, ps_meta = cls._capture_powershell(out)
            meta.update(ps_meta)
            if path:
                return path, meta

        meta["fallback_reason"] = "capture_unavailable"
        return None, meta

    @classmethod
    def execute_intent(cls, intent: ActionIntent) -> Tuple[str, Dict[str, Any]]:
        meta: Dict[str, Any] = {
            "source": "windows_desktop",
            "phase": "4D",
            "observable": True,
        }
        if cls._pyautogui_ok():
            from core.os_automation.driver import OsAutomationDriver

            return OsAutomationDriver.execute(intent)

        if not cls.automation_available():
            meta["fallback_reason"] = "desktop_automation_unavailable"
            return "[4D blocked] Windows 桌面自动化不可用", meta

        bounds = (intent.parameters or {}).get("bounds")
        x, y = cls._resolve_point(bounds)

        try:
            if intent.action_type == "click":
                cls._ps_click(x, y)
                label = intent.target_label or "target"
                meta["coordinates"] = {"x": x, "y": y}
                meta["live"] = True
                return f"[live-win] click「{label}」@({x},{y})", meta

            if intent.action_type == "focus":
                cls._ps_click(x, y)
                meta["live"] = True
                return f"[live-win] focus @({x},{y})", meta

            if intent.action_type == "type_text":
                text = str((intent.parameters or {}).get("text", ""))
                cls._ps_click(x, y)
                cls._ps_type(text)
                meta["live"] = True
                return f"[live-win] type「{text[:40]}」", meta

            if intent.action_type == "navigate":
                cls._ps_hotkey("%", "{TAB}")
                meta["live"] = True
                return "[live-win] alt+tab navigate", meta

            if intent.action_type == "scroll":
                clicks = int((intent.parameters or {}).get("clicks", -3))
                cls._ps_scroll(clicks)
                meta["live"] = True
                return f"[live-win] scroll {clicks}", meta

            raise ValueError(f"Unsupported action: {intent.action_type}")
        except Exception as exc:
            meta["error"] = str(exc)
            meta["fallback_reason"] = "powershell_automation_failed"
            raise

    @classmethod
    def _pyautogui_ok(cls) -> bool:
        if cls.is_wsl():
            return False
        try:
            import pyautogui  # noqa: F401

            return True
        except ImportError:
            return False

    @classmethod
    def _capture_powershell(cls, out: Path) -> Tuple[Optional[str], Dict[str, Any]]:
        meta: Dict[str, Any] = {"source": "powershell_capture"}
        win_out = cls.to_windows_path(out)
        ps = (
            "Add-Type -AssemblyName System.Windows.Forms,System.Drawing; "
            "$b=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds; "
            "$bmp=New-Object Drawing.Bitmap $b.Width,$b.Height; "
            "$g=[Drawing.Graphics]::FromImage($bmp); "
            "$g.CopyFromScreen($b.Location,[Drawing.Point]::Empty,$b.Size); "
            f"$bmp.Save('{win_out}'); $g.Dispose(); $bmp.Dispose()"
        )
        ok = cls._run_powershell(ps)
        if ok:
            if out.is_file():
                meta["path"] = str(out)
                return str(out), meta
            wp = Path(win_out)
            if wp.is_file():
                meta["windows_path"] = win_out
                meta["path"] = win_out
                return win_out, meta
        meta["fallback_reason"] = "powershell_capture_failed"
        return None, meta

    @classmethod
    def _ps_click(cls, x: int, y: int) -> None:
        ps = (
            "Add-Type @'\n"
            "using System; using System.Runtime.InteropServices;\n"
            "public class WdMouse {\n"
            " [DllImport(\"user32.dll\")] public static extern bool SetCursorPos(int X,int Y);\n"
            " [DllImport(\"user32.dll\")] public static extern void mouse_event(uint f,int dx,int dy,uint c,int e);\n"
            "}\n"
            "'@; "
            f"[WdMouse]::SetCursorPos({x},{y}); "
            "[WdMouse]::mouse_event(0x0002,0,0,0,0); "
            "[WdMouse]::mouse_event(0x0004,0,0,0,0)"
        )
        if not cls._run_powershell(ps):
            raise RuntimeError("powershell click failed")

    @classmethod
    def _ps_type(cls, text: str) -> None:
        escaped = cls._escape_sendkeys(text)
        ps = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            f"[System.Windows.Forms.SendKeys]::SendWait('{escaped}')"
        )
        if not cls._run_powershell(ps):
            raise RuntimeError("powershell type failed")

    @classmethod
    def _ps_hotkey(cls, *keys: str) -> None:
        combo = "".join(keys)
        ps = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            f"[System.Windows.Forms.SendKeys]::SendWait('{combo}')"
        )
        if not cls._run_powershell(ps):
            raise RuntimeError("powershell hotkey failed")

    @classmethod
    def _ps_scroll(cls, clicks: int) -> None:
        delta = -120 * int(clicks) if clicks else -360
        ps = (
            "Add-Type @'\n"
            "using System; using System.Runtime.InteropServices;\n"
            "public class WdWheel {\n"
            " [DllImport(\"user32.dll\")] public static extern void mouse_event(uint f,int dx,int dy,uint c,int e);\n"
            "}\n"
            "'@; "
            f"[WdWheel]::mouse_event(0x0800,0,0,{delta},0)"
        )
        if not cls._run_powershell(ps):
            raise RuntimeError("powershell scroll failed")

    @staticmethod
    def _run_powershell(command: str) -> bool:
        exe = "powershell.exe" if WindowsDesktop.is_wsl() else "powershell"
        try:
            r = subprocess.run(
                [exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
                capture_output=True,
                text=True,
                timeout=45,
            )
            return r.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False

    @classmethod
    def to_windows_path(cls, path: Path | str) -> str:
        """WSL /mnt/c/... → C:\\... for explorer.exe / cmd (never \\mnt\\c\\...)."""
        p = Path(path).resolve()
        try:
            r = subprocess.run(
                ["wslpath", "-w", str(p)],
                capture_output=True,
                text=True,
                timeout=5,
                check=True,
            )
            return r.stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            pass
        return cls._to_windows_path(p)

    @staticmethod
    def _to_windows_path(path: Path) -> str:
        p = str(path)
        if p.startswith("/mnt/"):
            parts = p.split("/")
            if len(parts) >= 4:
                drive = parts[2].upper()
                rest = "\\".join(parts[3:])
                return f"{drive}:\\{rest}"
        return p.replace("/", "\\")

    @classmethod
    def open_in_windows_shell(cls, path: Path | str) -> bool:
        p = Path(path)
        if not p.is_file():
            return False
        win = cls.to_windows_path(p)
        if cls.is_wsl():
            try:
                subprocess.run(
                    ["explorer.exe", win],
                    check=False,
                    timeout=15,
                )
                return True
            except OSError:
                pass
        if cls.is_windows_native():
            os.startfile(win)  # type: ignore[attr-defined]
            return True
        return False

    @staticmethod
    def _escape_sendkeys(text: str) -> str:
        out = []
        for ch in text[:500]:
            if ch in ("+", "^", "%", "~", "(", ")", "{", "}", "[", "]"):
                out.append("{" + ch + "}")
            else:
                out.append(ch)
        return "".join(out)

    @classmethod
    def _resolve_point(cls, bounds: Optional[Dict]) -> Tuple[int, int]:
        if isinstance(bounds, dict):
            x, y = bounds.get("x"), bounds.get("y")
            w = bounds.get("w", bounds.get("width", 0)) or 0
            h = bounds.get("h", bounds.get("height", 0)) or 0
            if x is not None and y is not None:
                return int(x) + int(w) // 2, int(y) + int(h) // 2
        if cls._pyautogui_ok():
            import pyautogui

            size = pyautogui.size()
            return size.width // 2, size.height // 2
        return 960, 540

    @staticmethod
    def parse_bounds(raw: Any) -> Optional[Dict[str, int]]:
        if isinstance(raw, dict) and raw.get("x") is not None:
            return {
                "x": int(raw["x"]),
                "y": int(raw["y"]),
                "w": int(raw.get("w", raw.get("width", 10))),
                "h": int(raw.get("h", raw.get("height", 10))),
            }
        if isinstance(raw, str):
            nums = [int(n) for n in re.findall(r"-?\d+", raw)[:4]]
            if len(nums) >= 4:
                return {"x": nums[0], "y": nums[1], "w": nums[2], "h": nums[3]}
            if len(nums) >= 2:
                return {"x": nums[0], "y": nums[1], "w": 10, "h": 10}
        return None
