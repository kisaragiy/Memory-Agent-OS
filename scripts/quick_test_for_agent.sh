#!/usr/bin/env bash
# 快速测试（无 start-server、无 pytest）— 供 Agent 拉取结果，约 2–5 分钟
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT="$ROOT/docs/test_runs/quick_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUT"
echo "$OUT" > "$ROOT/docs/test_runs/LATEST.txt"

if [ -f .venv/bin/activate ]; then source .venv/bin/activate; fi

{
  echo "=== QUICK TEST $(date -Iseconds) ==="
  echo "OUT=$OUT"
  curl -s -m 5 http://127.0.0.1:8787/api/health || echo "HEALTH_FAIL"
  python3 -m pytest tests/ -q --tb=no -x 2>&1 | tail -20
  PY=$?
  echo "PYTEST_EXIT=$PY"
  pip install -q -r requirements-test-capture.txt 2>&1 | tail -3
  python3 -m playwright install chromium 2>&1 | tail -2
  if curl -s -m 3 http://127.0.0.1:8787/api/health >/dev/null 2>&1; then
    EXTRA=(--no-pytest)
  else
    EXTRA=(--no-pytest --start-server)
  fi
  python3 scripts/background_test_capture.py --browser-only --out-dir "$OUT" "${EXTRA[@]}" 2>&1
  echo "CAPTURE_EXIT=$?"
} > "$OUT/run.log" 2>&1

cp "$OUT/run.log" "$ROOT/docs/test_runs/last_run_stdout.log"
echo "$(tail -1 "$OUT/run.log" | grep -o 'CAPTURE_EXIT=[0-9]*' || echo EXIT:1)" > "$ROOT/docs/test_runs/last_exit_code.txt"
cat "$OUT/summary.json" 2>/dev/null > "$ROOT/docs/test_runs/last_summary.json" || true
ls "$OUT/screenshots/" 2>/dev/null > "$ROOT/docs/test_runs/last_screenshots.txt" || true
echo DONE >> "$OUT/run.log"
