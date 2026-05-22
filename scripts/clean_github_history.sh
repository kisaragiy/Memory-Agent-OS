#!/usr/bin/env bash
# 合并为一条干净提交说明，并推送到 GitHub
set -e
cd /home/zwq/AgentOSSystem
export GIT_AUTHOR_NAME="张伟强"
export GIT_AUTHOR_EMAIL="126777810+kisaragiy@users.noreply.github.com"

git rm -rf --cached --ignore-unmatch \
  "File: core/runtime/agent_os_runtime.py" \
  "File: core/runtime/execution_engine.py" \
  "File: core/runtime/observability.py" \
  "Output capability registry list (debug)" 2>/dev/null || true

git checkout --orphan portfolio-clean
git add -A
git commit -m "feat: Memory Agent OS — single-kernel LLM agent runtime"
git branch -M main
git push -u origin main --force
git log -1 --oneline
echo "OK: https://github.com/kisaragiy/Memory-Agent-OS"
