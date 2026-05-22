#!/usr/bin/env bash
# 在 WSL 终端内运行（不要在此环境运行 .ps1）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export AGENT_WINDOWS_DESKTOP=1
export AUTONOMOUS_CAPTURE=1
export USE_VISION_OBSERVER=1
export AGENT_AUTONOMOUS=1
export AGENT_CONTROL_MODE=developer
export GUARDED_UI_LIVE="${GUARDED_UI_LIVE:-1}"
export AGENT_SERVICE_HOST="${AGENT_SERVICE_HOST:-127.0.0.1}"
export AGENT_SERVICE_PORT="${AGENT_SERVICE_PORT:-8787}"

echo "=============================================="
echo " Memory Chat — WSL + Windows 桌面"
echo " GUARDED_UI_LIVE=$GUARDED_UI_LIVE"
echo " 实况流:    http://${AGENT_SERVICE_HOST}:${AGENT_SERVICE_PORT}/api/desktop/stream"
echo " 单帧:      http://${AGENT_SERVICE_HOST}:${AGENT_SERVICE_PORT}/api/desktop/screenshot"
echo " Web UI:    http://${AGENT_SERVICE_HOST}:${AGENT_SERVICE_PORT}/app/  (开发者模式 → 桌面实况)"
echo "=============================================="
echo ""

if ! python3 scripts/verify_desktop_capture.py; then
  echo "截屏验证失败，请先修复后再启动服务。"
  exit 1
fi

echo ""
echo "启动 agent_service …"
exec python3 -m agent_service
