#!/usr/bin/env bash
# 后台测试+截图 — 可 nohup 挂起，你去别的窗口工作即可
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [ -d .venv ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi
export AGENT_WINDOWS_DESKTOP=1
export AUTONOMOUS_CAPTURE=1
export AGENT_SERVICE_URL="${AGENT_SERVICE_URL:-http://127.0.0.1:8787}"

TS="$(date +%Y%m%d_%H%M%S)"
LOG="$ROOT/docs/test_runs/background_${TS}.log"
mkdir -p "$ROOT/docs/test_runs"

if [ "${1:-}" = "--detach" ]; then
  shift
  nohup python3 scripts/background_test_capture.py "$@" >>"$LOG" 2>&1 &
  echo "后台 PID $! — 日志: $LOG"
  echo "完成后查看: docs/test_runs/LATEST.txt"
  exit 0
fi

exec python3 scripts/background_test_capture.py --browser-only "$@"
