# Foreground dev launcher — Windows desktop vision + guarded automation.
# Run with **Windows Python** (recommended) or WSL Python (capture via PowerShell bridge).

param(
    [int]$Port = 8787,
    [string]$BindHost = "127.0.0.1",
    [switch]$Autonomous,
    [switch]$Live,
    [switch]$Desktop
)

$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location $Root

$env:AGENT_SERVICE_PORT = "$Port"
$env:AGENT_SERVICE_HOST = $BindHost
$env:AGENT_STATIC_DIR = Join-Path $Root "web"

# Windows desktop: see host screen + optional live mouse/keyboard
$env:AGENT_WINDOWS_DESKTOP = "1"
$env:AUTONOMOUS_CAPTURE = "1"
$env:USE_VISION_OBSERVER = "1"

if ($Autonomous) { $env:AGENT_AUTONOMOUS = "1" }
if ($Live) { $env:GUARDED_UI_LIVE = "1" }
if ($Desktop -and -not $Autonomous) {
    Write-Host "Desktop mode: vision capture on; use -Autonomous -Live for auto UI actions."
}

Write-Host "Agent OS — Windows desktop mode"
Write-Host "  http://${BindHost}:$Port/app/"
Write-Host "  GUARDED_UI_LIVE=$($env:GUARDED_UI_LIVE)"
Write-Host "  AGENT_AUTONOMOUS=$($env:AGENT_AUTONOMOUS)"
Write-Host ""

python -m agent_service
