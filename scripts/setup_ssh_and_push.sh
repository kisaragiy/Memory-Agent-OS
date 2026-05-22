#!/usr/bin/env bash
# 一次性：修复 SSH known_hosts + 显示公钥 + 尝试推送
set -e
ROOT="/home/zwq/AgentOSSystem"
cd "$ROOT"
mkdir -p ~/.ssh
chmod 700 ~/.ssh
if [ ! -f ~/.ssh/id_ed25519 ]; then
  ssh-keygen -t ed25519 -C "taqibala@outlook.com" -f ~/.ssh/id_ed25519 -N ""
fi
ssh-keyscan -t ed25519,rsa github.com >> ~/.ssh/known_hosts 2>/dev/null || true
chmod 600 ~/.ssh/known_hosts 2>/dev/null || true

echo ""
echo "========== 复制下面整行到 GitHub → Settings → SSH keys =========="
cat ~/.ssh/id_ed25519.pub
echo "================================================================="
echo ""

git remote set-url origin git@github.com:kisaragiy/Memory-Agent-OS.git
BRANCH="$(git branch --show-current)"
echo "测试连接…"
ssh -T git@github.com || true
echo "推送 $BRANCH …"
git push -u origin "$BRANCH"
echo "完成: https://github.com/kisaragiy/Memory-Agent-OS"
