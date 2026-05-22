#!/usr/bin/env bash
# Push to https://github.com/kisaragiy/Memory-Agent-OS (no resume PDF)
set -e
_SCRIPT="$(readlink -f "${BASH_SOURCE[0]}" 2>/dev/null || echo "${BASH_SOURCE[0]}")"
ROOT="$(cd "$(dirname "$_SCRIPT")/.." && pwd)"
# When invoked from Windows UNC / drvfs, use Linux path
case "$ROOT" in
  *wsl.localhost*|//*) ROOT="/home/zwq/AgentOSSystem" ;;
esac
cd "$ROOT" || { echo "Cannot cd to $ROOT"; exit 1; }
REMOTE_URL="${REMOTE_URL:-https://github.com/kisaragiy/Memory-Agent-OS.git}"
LOG="$ROOT/scripts/push_github_result.txt"
: > "$LOG"

log() { echo "$1" | tee -a "$LOG"; }

log "=== $(date -Iseconds) push_github ==="
log "ROOT=$ROOT"

# Stop tracking resume PDF if it was committed before
git rm -r --cached docs/*.pdf 2>/dev/null || true
git rm --cached "docs/"*".pdf" 2>/dev/null || true

if git remote get-url origin &>/dev/null; then
  git remote set-url origin "$REMOTE_URL"
else
  git remote add origin "$REMOTE_URL"
fi
log "remote: $(git remote get-url origin)"

git add -A
log "=== git status (short) ==="
git status --short | head -60 | tee -a "$LOG"

if git diff --cached --quiet && git diff --quiet; then
  log "Nothing to commit."
else
  export GIT_AUTHOR_NAME="${GIT_AUTHOR_NAME:-张伟强}"
  export GIT_AUTHOR_EMAIL="${GIT_AUTHOR_EMAIL:-taqibala@outlook.com}"
  export GIT_COMMITTER_NAME="${GIT_COMMITTER_NAME:-张伟强}"
  export GIT_COMMITTER_EMAIL="${GIT_COMMITTER_EMAIL:-taqibala@outlook.com}"
  git commit -m "$(cat <<'EOF'
chore: publish portfolio — docs, gitignore, exclude resume PDF

- HR test cases, GitHub upload guide
- Ignore memory_db, test_runs, resume PDF
- Align with public Memory-Agent-OS repo
EOF
)"
  log "committed: $(git log -1 --oneline)"
fi

BRANCH="$(git branch --show-current)"
[ -n "$BRANCH" ] || BRANCH=master

log "=== git push -u origin $BRANCH ==="
if git push -u origin "$BRANCH" 2>&1 | tee -a "$LOG"; then
  log "OK: https://github.com/kisaragiy/Memory-Agent-OS"
  exit 0
else
  log "FAIL: push failed — check auth (gh auth login or SSH key)"
  exit 1
fi
