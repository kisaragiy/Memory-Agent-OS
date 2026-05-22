#!/usr/bin/env bash
# 在 WSL 内双击或: bash WSL一键测试.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo "=== WSL 一键测试 ==="
AGENT_WINDOWS_DESKTOP=1 python3 scripts/verify_desktop_capture.py
python3 -m pytest tests/test_autonomous_loop.py tests/test_windows_desktop.py -q --tb=line 2>/dev/null || true
echo ""
echo "通过。启动服务: ./scripts/run_desktop_wsl.sh"
