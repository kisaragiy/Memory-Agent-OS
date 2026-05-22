# PowerShell 入口（与 .sh 等价）— 在 PS 里运行本文件，不要用 GUARDED_UI_LIVE=1 ./xxx.sh
param([switch]$Live)

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$env:AGENT_WINDOWS_DESKTOP = "1"
$env:AUTONOMOUS_CAPTURE = "1"
$env:USE_VISION_OBSERVER = "1"
$env:AGENT_AUTONOMOUS = "1"
$env:AGENT_CONTROL_MODE = "developer"
if ($Live) { $env:GUARDED_UI_LIVE = "1" }

Write-Host "通过 WSL 启动 agent_service …"
if ($Live) {
    wsl -d Ubuntu-22.04 bash -lc "cd /home/zwq/memory-chat && export GUARDED_UI_LIVE=1 AGENT_WINDOWS_DESKTOP=1 AUTONOMOUS_CAPTURE=1 USE_VISION_OBSERVER=1 AGENT_AUTONOMOUS=1 AGENT_CONTROL_MODE=developer; exec python3 -m agent_service"
} else {
    wsl -d Ubuntu-22.04 bash -lc "cd /home/zwq/memory-chat && export AGENT_WINDOWS_DESKTOP=1 AUTONOMOUS_CAPTURE=1 USE_VISION_OBSERVER=1 AGENT_AUTONOMOUS=1 AGENT_CONTROL_MODE=developer; exec python3 -m agent_service"
}
