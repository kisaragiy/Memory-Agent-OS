# Install Memory Agent OS as a Windows Service (requires Administrator).
# Uses NSSM if available, otherwise sc.exe + pythonw.

param(
    [string]$ServiceName = "MemoryAgentOS",
    [string]$InstallRoot = "",
    [int]$Port = 8787,
    [switch]$Autonomous,
    [switch]$Live
)

$ErrorActionPreference = "Stop"

if (-not $InstallRoot) {
    $InstallRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
}

$pyCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pyCmd) { $python = $pyCmd.Source } else { $python = $null }
if (-not $python) {
    $py3 = Get-Command python3 -ErrorAction SilentlyContinue
    if ($py3) { $python = $py3.Source }
}
if (-not $python) {
    throw "Python not found on PATH. Install Python 3.10+ for Windows."
}

$envBlock = @(
    "AGENT_SERVICE_PORT=$Port",
    "AGENT_SERVICE_HOST=127.0.0.1",
    "AGENT_STATIC_DIR=$InstallRoot\web"
)
if ($Autonomous) { $envBlock += "AGENT_AUTONOMOUS=1" }
if ($Live) { $envBlock += "GUARDED_UI_LIVE=1" }

$moduleArgs = "-m agent_service"
$nssm = Get-Command nssm -ErrorAction SilentlyContinue

Write-Host "Install root: $InstallRoot"
Write-Host "Python: $python"
Write-Host "Port: $Port"

if ($nssm) {
    & nssm install $ServiceName $python $moduleArgs
    & nssm set $ServiceName AppDirectory $InstallRoot
    & nssm set $ServiceName AppEnvironmentExtra ($envBlock -join "`n")
    & nssm set $ServiceName DisplayName "Memory Agent OS"
    & nssm set $ServiceName Description "Agent OS runtime HTTP service (single kernel)"
    & nssm set $ServiceName Start SERVICE_AUTO_START
    Write-Host "Installed via NSSM. Start: nssm start $ServiceName"
} else {
    $binPath = "`"$python`" $moduleArgs"
    sc.exe create $ServiceName binPath= $binPath start= auto DisplayName= "Memory Agent OS"
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "sc.exe create may need manual env vars. Prefer NSSM: https://nssm.cc/download"
    }
    Write-Host "Created service $ServiceName (set AGENT_* env in System Properties if needed)."
}

Write-Host @"

Next steps:
  1. pip install -r requirements.txt  (in $InstallRoot)
  2. Start service:  Start-Service $ServiceName  OR  nssm start $ServiceName
  3. Open UI: http://127.0.0.1:$Port/
  4. Health: http://127.0.0.1:$Port/api/health

Dev (foreground):  cd $InstallRoot; python -m agent_service
"@
