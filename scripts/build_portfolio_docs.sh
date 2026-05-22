#!/usr/bin/env bash
# Generate architecture PNGs and docx under docs/
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [ -d .venv ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi
pip install -q -r requirements-docs.txt
python3 scripts/generate_portfolio_docs.py
