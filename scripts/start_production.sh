#!/usr/bin/env bash
# Production: serve built React UI + Agent OS API on :8787
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ ! -f web/frontend/dist/index.html ]; then
  echo "Building frontend…"
  (cd web/frontend && npm run build)
fi

export AGENT_REACT_DIST="$ROOT/web/frontend/dist"
export AGENT_STATIC_DIR="$ROOT/web"
echo "Starting Agent OS at http://127.0.0.1:8787/app/"
exec python3 -m agent_service
