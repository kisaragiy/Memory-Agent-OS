@echo off
REM 绕过 UNC + 执行策略限制
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Verify-DesktopCapture.ps1" %*
