# 将本目录全部脚本复制到「桌面\OS」
$ErrorActionPreference = "Stop"
$src = $PSScriptRoot
$dest = Join-Path ([Environment]::GetFolderPath("Desktop")) "OS"
New-Item -ItemType Directory -Path $dest -Force | Out-Null
Copy-Item -Path (Join-Path $src "*") -Destination $dest -Recurse -Force
Write-Host "已安装到: $dest" -ForegroundColor Green
Write-Host "请从桌面\OS 运行脚本（不要从 \\wsl.localhost\... 直接双击）" -ForegroundColor Yellow
Write-Host "首次建议: 0-诊断环境.cmd -> 后台自动测试截图.cmd" -ForegroundColor Cyan
explorer.exe $dest
