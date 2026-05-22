#!/usr/bin/env python3
"""
截屏验证 — 保存截图并在 Windows 中打开（WSL 用 explorer.exe + C:\\ 路径）。

在 WSL 内运行:
  python3 scripts/verify_desktop_capture.py

在 Windows PowerShell 内运行（不要先 wsl）:
  .\\scripts\\windows\\Verify-DesktopCapture.cmd
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("AGENT_WINDOWS_DESKTOP", "1")
os.environ.setdefault("AUTONOMOUS_CAPTURE", "1")

from core.platform.windows_desktop import WindowsDesktop


def _default_out() -> Path:
    if WindowsDesktop.is_wsl():
        for guess in (
            Path("/mnt/c/Users/Public/Desktop/memory_chat_verify.png"),
            Path("/mnt/c/Users/Public/memory_chat_verify.png"),
        ):
            if guess.parent.exists():
                return guess
    return Path.home() / "memory_chat_verify.png"


def main() -> int:
    print("=== Desktop capture verify ===")
    print(f"  WSL: {WindowsDesktop.is_wsl()}")
    print(f"  Windows native: {WindowsDesktop.is_windows_native()}")
    print(f"  automation_available: {WindowsDesktop.automation_available()}")

    path, meta = WindowsDesktop.capture_screenshot(_default_out())
    print(f"  capture meta: {meta}")
    if not path:
        print("\nFAIL: 无法截屏。请在 Windows PowerShell 运行:")
        print("  scripts\\windows\\Verify-DesktopCapture.cmd")
        return 1

    p = Path(path)
    win_path = WindowsDesktop.to_windows_path(p)
    print(f"\nOK (WSL path): {p}")
    print(f"   Windows 路径: {win_path}")
    if p.is_file():
        print(f"   size: {p.stat().st_size} bytes")

    if WindowsDesktop.open_in_windows_shell(p):
        print("\n已用 explorer.exe 打开 — 请目视确认是否为当前 Windows 桌面。")
    else:
        print(f"\n请手动在资源管理器打开: {win_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
