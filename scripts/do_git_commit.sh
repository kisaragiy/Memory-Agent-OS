#!/bin/bash
cd /home/zwq/AgentOSSystem
chown -R zwq:zwq docs/ scripts/run_result.txt 2>/dev/null || true
export GIT_AUTHOR_NAME="张伟强"
export GIT_AUTHOR_EMAIL="taqibala@outlook.com"
export GIT_COMMITTER_NAME="张伟强"
export GIT_COMMITTER_EMAIL="taqibala@outlook.com"
{
  git add README.md PORTFOLIO.md LICENSE .gitignore legacy/README.md docs/ scripts/generate_resume_pdf.py scripts/build_resume.bat core/memory/vector_store.py
  echo "=== git status --short ==="
  git status --short | head -20
  echo "=== git commit --trailer "Co-authored-by: Cursor <cursoragent@cursor.com>" ==="
  git commit --trailer "Co-authored-by: Cursor <cursoragent@cursor.com>" -m "chore: portfolio docs, resume PDF, README"
  echo "=== git log -1 --oneline ==="
  git log -1 --oneline
} > scripts/git_result.txt 2>&1
cat scripts/git_result.txt