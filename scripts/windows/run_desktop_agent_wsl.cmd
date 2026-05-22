@echo off
REM 推荐：在 Windows PowerShell 中启动 WSL 里的 agent（避免 UNC 下跑 .ps1）
echo Starting Agent OS in WSL with Windows desktop capture...
wsl -d Ubuntu-22.04 bash -lc "cd /home/zwq/memory-chat && GUARDED_UI_LIVE=1 AGENT_WINDOWS_DESKTOP=1 AUTONOMOUS_CAPTURE=1 USE_VISION_OBSERVER=1 AGENT_AUTONOMOUS=1 AGENT_CONTROL_MODE=developer exec python3 -m agent_service"
pause
