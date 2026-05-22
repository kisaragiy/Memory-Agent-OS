# 目视验证：截取 Windows 主屏并自动打开图片（不依赖 WSL / Python）
param(
    [string]$OutFile = "$env:USERPROFILE\Desktop\memory_chat_verify.png"
)

$ErrorActionPreference = "Stop"
Write-Host "=== Memory Chat — Windows 桌面截屏验证 ===" -ForegroundColor Cyan

Add-Type -AssemblyName System.Windows.Forms,System.Drawing
$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
Write-Host "主屏分辨率: $($bounds.Width) x $($bounds.Height)"

$bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
$graphics = [System.Drawing.Graphics]::FromImage($bmp)
$graphics.CopyFromScreen($bounds.Location, [Drawing.Point]::Empty, $bounds.Size)
$graphics.Dispose()

$dir = Split-Path $OutFile -Parent
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
$bmp.Save($OutFile, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()

$fi = Get-Item $OutFile
Write-Host "已保存: $($fi.FullName)  ($([math]::Round($fi.Length/1KB)) KB)" -ForegroundColor Green
Write-Host "正在打开图片…若能看到当前桌面，说明 OS 可以「看到」Windows 画面。" -ForegroundColor Yellow
Start-Process $fi.FullName

Write-Host ""
Write-Host "下一步（Windows 原生 Python，推荐）:" -ForegroundColor Cyan
Write-Host "  cd $PSScriptRoot\..\.."
Write-Host "  .\scripts\windows\run_desktop_agent.ps1"
