#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
echo "=== Git status ==="
git status -sb 2>&1 | head -40
echo ""
echo "=== Remote ==="
git remote -v 2>&1 || true
echo ""
echo "=== Pytest quick ==="
python3 -m pytest tests/ -q --tb=no 2>&1 | tail -5
