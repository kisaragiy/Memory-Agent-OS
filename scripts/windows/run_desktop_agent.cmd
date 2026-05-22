@echo off
REM 从 \\wsl.localhost\... UNC 路径也可运行（无需 Set-ExecutionPolicy）
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_desktop_agent.ps1" %*
