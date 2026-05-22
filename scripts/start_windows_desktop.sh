#!/usr/bin/env bash
# WSL: capture/automate the **Windows host** desktop via PowerShell bridge.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export AGENT_WINDOWS_DESKTOP=1
export AUTONOMOUS_CAPTURE=1
export USE_VISION_OBSERVER=1
export AGENT_AUTONOMOUS="${AGENT_AUTONOMOUS:-1}"
export GUARDED_UI_LIVE="${GUARDED_UI_LIVE:-0}"
export AGENT_CONTROL_MODE="${AGENT_CONTROL_MODE:-developer}"

exec bash "$(dirname "$0")/run_desktop_wsl.sh"
