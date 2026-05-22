#!/usr/bin/env bash
# 测试结束后在 WSL 运行，打印冒烟测试摘要
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LATEST="$ROOT/docs/test_runs/LATEST.txt"
echo "========== Memory Agent OS 测试结果 =========="
if [ -f "$ROOT/docs/test_runs/last_exit_code.txt" ]; then
  echo "退出码: $(cat "$ROOT/docs/test_runs/last_exit_code.txt")"
fi
if [ -f "$LATEST" ]; then
  RUN=$(cat "$LATEST")
  echo "报告目录: $RUN"
  [ -f "$RUN/test_report.html" ] && echo "报告: $RUN/test_report.html"
  if [ -f "$RUN/summary.json" ]; then
    export RUN
    python3 - <<'PY'
import json, pathlib, os
root = pathlib.Path(os.environ["RUN"])
s = json.loads((root / "summary.json").read_text(encoding="utf-8"))
print("\n【分步结果】")
for st in s.get("steps", []):
    mark = "通过" if st.get("ok") else "未通过"
    print(f"  {st.get('id','?')} {st.get('title_hr','')} -> {mark}")
py = s.get("pytest", {})
if py:
    print(f"\n【pytest】 {'通过' if py.get('ok') else '失败'}")
PY
  fi
  echo -e "\n【截图文件】"
  ls -1 "$RUN/screenshots/" 2>/dev/null || echo "  (无)"
fi
echo "============================================="
