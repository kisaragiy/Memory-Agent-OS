#!/usr/bin/env bash
# 自动推送到 GitHub：HTTPS 直连/代理 → SSH → Windows Git
set -u
ROOT="/home/zwq/AgentOSSystem"
cd "$ROOT" || exit 1
LOG="$ROOT/scripts/push_github_auto.log"
: > "$LOG"

HTTPS_REMOTE="https://github.com/kisaragiy/Memory-Agent-OS.git"
SSH_REMOTE="git@github.com:kisaragiy/Memory-Agent-OS.git"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }

BRANCH="$(git branch --show-current)"
[ -n "$BRANCH" ] || BRANCH=main
log "分支: $BRANCH | 本地: $(git log -1 --oneline 2>/dev/null || echo '?')"

git config --global http.postBuffer 524288000 2>/dev/null || true
git config --global http.lowSpeedLimit 0 2>/dev/null || true
git config --global http.lowSpeedTime 999999 2>/dev/null || true

can_reach_github() {
  curl -fsSI --connect-timeout 10 --max-time 20 https://github.com >/dev/null 2>&1
}

setup_proxy() {
  local host="$1" port="$2"
  export http_proxy="http://${host}:${port}"
  export https_proxy="http://${host}:${port}"
  git config --global http.proxy "http://${host}:${port}"
  git config --global https.proxy "http://${host}:${port}"
}

clear_proxy() {
  unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY 2>/dev/null || true
  git config --global --unset http.proxy 2>/dev/null || true
  git config --global --unset https.proxy 2>/dev/null || true
}

verify_pushed() {
  LOCAL_SHA="$(git rev-parse "$BRANCH" 2>/dev/null)" || return 1
  REMOTE_SHA="$(git ls-remote origin "refs/heads/$BRANCH" 2>/dev/null | awk '{print $1}')"
  log "校验 remote=$REMOTE_SHA local=$LOCAL_SHA"
  [ -n "$REMOTE_SHA" ] && [ "$REMOTE_SHA" = "$LOCAL_SHA" ]
}

try_push_remote() {
  local label="$1" remote_url="$2"
  git remote set-url origin "$remote_url"
  log "=== $label | $remote_url ==="
  git fetch origin 2>>"$LOG" || true
  git push -u origin "$BRANCH" 2>&1 | tee -a "$LOG"
  local ec=${PIPESTATUS[0]}
  if [ "$ec" -eq 0 ] && verify_pushed; then
    log "OK: https://github.com/kisaragiy/Memory-Agent-OS"
    exit 0
  fi
  log "push 失败或未同步 (exit=$ec)"
  return 1
}

run_with_network() {
  local net_label="$1"
  try_push_remote "${net_label} HTTPS" "$HTTPS_REMOTE" && return 0
  if [ -f "$HOME/.ssh/id_ed25519" ] || [ -f "$HOME/.ssh/id_rsa" ]; then
    export GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=accept-new"
    try_push_remote "${net_label} SSH" "$SSH_REMOTE" && return 0
  else
    log "跳过 SSH（无 ~/.ssh/id_ed25519）"
  fi
  return 1
}

# --- 1) 直连 ---
clear_proxy
if can_reach_github; then
  log "网络可达 GitHub（直连）"
  run_with_network "直连" && exit 0
else
  log "直连 curl 失败，探测代理…"
fi

# --- 2) Windows 主机代理端口 ---
HOST_IP="$(grep -m1 nameserver /etc/resolv.conf | awk '{print $2}')"
log "Windows IP: ${HOST_IP:-?}"
for PORT in 7897 7890 10809 10808 8080 8118; do
  clear_proxy
  setup_proxy "$HOST_IP" "$PORT"
  if can_reach_github; then
    log "代理通: ${HOST_IP}:${PORT}"
    run_with_network "代理:$PORT" && exit 0
  fi
done
clear_proxy

# --- 3) Windows Git（TUN / 系统代理）---
WIN_GIT=""
for p in \
  "/mnt/c/Program Files/Git/cmd/git.exe" \
  "/mnt/c/Program Files/Git/bin/git.exe"; do
  [ -x "$p" ] && WIN_GIT="$p" && break
done
if [ -n "$WIN_GIT" ]; then
  WIN_ROOT="$(wslpath -w "$ROOT")"
  log "=== Windows Git: $WIN_GIT ==="
  "$WIN_GIT" -C "$WIN_ROOT" config --global --add safe.directory "$WIN_ROOT" 2>>"$LOG" || true
  for R in "$HTTPS_REMOTE" "$SSH_REMOTE"; do
    "$WIN_GIT" -C "$WIN_ROOT" remote set-url origin "$R" 2>>"$LOG"
    "$WIN_GIT" -C "$WIN_ROOT" push -u origin "$BRANCH" 2>&1 | tee -a "$LOG"
    ec=${PIPESTATUS[0]}
    if [ "$ec" -eq 0 ]; then
      REMOTE_SHA="$("$WIN_GIT" -C "$WIN_ROOT" ls-remote origin "refs/heads/$BRANCH" 2>/dev/null | awk '{print $1}')"
      LOCAL_SHA="$(git rev-parse "$BRANCH")"
      log "WinGit remote=$REMOTE_SHA local=$LOCAL_SHA"
      [ "$REMOTE_SHA" = "$LOCAL_SHA" ] && { log "OK (Windows Git)"; exit 0; }
    fi
  done
fi

log "FAIL: 全部失败。"
log "1) 添加 SSH 公钥: cat ~/.ssh/id_ed25519.pub → https://github.com/settings/keys"
log "2) 或开 Clash「允许局域网」后重跑本脚本"
log "3) 修复 known_hosts: ssh-keyscan -t ed25519 github.com >> ~/.ssh/known_hosts"
exit 1
