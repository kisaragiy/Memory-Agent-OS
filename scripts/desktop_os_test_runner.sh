#!/usr/bin/env bash
# 供 desktop-os-tests/*.cmd 调用 — 避免 cmd 一行命令过长/吞错误
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
LOG="${1:-$ROOT/docs/test_runs/last_cmd_install.log}"
mkdir -p "$(dirname "$LOG")"

if [ ! -f web/frontend/dist/index.html ]; then
  echo "=== build frontend (first time) ===" | tee -a "$LOG"
  if command -v npm >/dev/null 2>&1; then
    (cd web/frontend && npm run build) 2>&1 | tee -a "$LOG"
  else
    echo "WARN: npm 未安装，Playwright 可能打开空白页。请在本机执行: cd web/frontend && npm run build" | tee -a "$LOG"
  fi
fi

if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "=== pip install (test capture) ===" | tee -a "$LOG"
pip install -r requirements-test-capture.txt 2>&1 | tee -a "$LOG"

echo "=== playwright chromium ===" | tee -a "$LOG"
python3 -m playwright install chromium 2>&1 | tee -a "$LOG"

EXTRA=(--hr --browser-only --open-report)
if curl -s -m 3 http://127.0.0.1:8787/api/health >/dev/null 2>&1; then
  echo "=== service already up, skip --start-server ===" | tee -a "$LOG"
else
  EXTRA+=(--start-server)
fi
echo "=== background test ===" | tee -a "$LOG"
exec python3 scripts/background_test_capture.py "${EXTRA[@]}" --no-pytest
