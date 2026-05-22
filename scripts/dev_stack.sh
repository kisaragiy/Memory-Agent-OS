#!/usr/bin/env bash
# Start API + Vite dev UI (WSL/Linux)
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ ! -d web/frontend/node_modules ]; then
  (cd web/frontend && npm install)
fi

python3 -m agent_service &
API_PID=$!
trap "kill $API_PID 2>/dev/null" EXIT

sleep 1
cd web/frontend
npm run dev
