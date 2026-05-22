# Build React UI + launch Electron desktop (Windows native Python recommended).
param(
    [switch]$Dev,
    [string]$Python = ""
)

$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location $Root

if (-not (Test-Path "$Root\web\frontend\node_modules")) {
    Push-Location "$Root\web\frontend"
    npm install
    Pop-Location
}

if (-not $Dev) {
    Push-Location "$Root\web\frontend"
    npm run build
    Pop-Location
}

if ($Python) { $env:AGENT_PYTHON = $Python }

Push-Location "$Root\electron"
if (-not (Test-Path node_modules)) { npm install }

if ($Dev) {
    Write-Host "Dev: start API (python -m agent_service) and Vite (npm run dev) in separate terminals, then:"
    $env:AGENT_ELECTRON_DEV = "1"
} else {
    Remove-Item Env:AGENT_ELECTRON_DEV -ErrorAction SilentlyContinue
}

npm start
Pop-Location
