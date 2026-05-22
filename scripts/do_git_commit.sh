#!/bin/bash
cd /home/zwq/AgentOSSystem
chown -R zwq:zwq docs/ scripts/run_result.txt 2>/dev/null || true
export GIT_AUTHOR_NAME="kisaragiy"
export GIT_AUTHOR_EMAIL="kisaragiy@users.noreply.github.com"
export GIT_COMMITTER_NAME="kisaragiy"
export GIT_COMMITTER_EMAIL="kisaragiy@users.noreply.github.com"
{
  git add README.md PORTFOLIO.md LICENSE .gitignore legacy/README.md docs/ scripts/generate_resume_pdf.py scripts/build_resume.bat core/memory/vector_store.py
  echo "=== git status --short ==="
  git status --short | head -20
  git commit -m "chore: portfolio docs and README"
  echo "=== git log -1 --oneline ==="
  git log -1 --oneline
} > scripts/git_result.txt 2>&1
cat scripts/git_result.txt