#!/bin/bash
set -x
exec > /home/zwq/AgentOSSystem/scripts/run_result.txt 2>&1

cd /home/zwq/AgentOSSystem

# fonts for CJK PDF
sudo apt-get update -qq 2>/dev/null | tail -1
sudo apt-get install -y -qq fonts-wqy-zenhei python3-pip 2>/dev/null | tail -3

pip3 install reportlab pypdf -q
python3 scripts/generate_resume_pdf.py

# copy resume to Windows interview folder if mount exists
WIN="/mnt/c/面试"
if [ -d "$WIN" ]; then
  cp -f docs/kisaragiy-后端开发.pdf "$WIN/kisaragiy-后端开发.pdf"
  echo "copied to $WIN"
fi

# git commit --trailer "Co-authored-by: Cursor <cursoragent@cursor.com>"
export GIT_AUTHOR_NAME="kisaragiy"
export GIT_AUTHOR_EMAIL="kisaragiy@users.noreply.github.com"
export GIT_COMMITTER_NAME="kisaragiy"
export GIT_COMMITTER_EMAIL="kisaragiy@users.noreply.github.com"
git add README.md PORTFOLIO.md LICENSE .gitignore legacy/ docs/ scripts/generate_resume_pdf.py core/memory/vector_store.py 2>/dev/null || true
git commit -m "chore: portfolio docs and assets" 2>&1 || true
git log -1 --oneline 2>&1 || true

ls -la docs/
cat docs/resume_verify.txt 2>/dev/null || true

echo DONE