# 在 PowerShell 中启动（不要用 bash 的 VAR=1 ./x.sh 语法）
param(
    [switch]$Live,
    [switch]$VerifyOnly,
    [switch]$UseWslPython
)

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $Root

if ($VerifyOnly) {
    & (Join-Path $PSScriptRoot "Verify-DesktopCapture.ps1")
    exit $LASTEXITCODE
}

Write-Host "Step 1/2 — 截屏目视验证（PowerShell 直截 Windows 桌面）" -ForegroundColor Cyan
& (Join-Path $PSScriptRoot "Verify-DesktopCapture.ps1")
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host ""
Write-Host "Step 2/2 — 启动 Agent 服务" -ForegroundColor Cyan

if ($UseWslPython) {
    $liveFlag = if ($Live) { "GUARDED_UI_LIVE=1 " } else { "" }
    wsl -d Ubuntu-22.04 bash -lc "cd /home/zwq/memory-chat && ${liveFlag}AGENT_WINDOWS_DESKTOP=1 AUTONOMOUS_CAPTURE=1 USE_VISION_OBSERVER=1 AGENT_AUTONOMOUS=1 AGENT_CONTROL_MODE=developer ./scripts/start_windows_desktop.sh"
} else {
    $args = @()
    if ($Live) { $args += "-Live" }
    & (Join-Path $PSScriptRoot "run_desktop_agent.ps1") @args
}
