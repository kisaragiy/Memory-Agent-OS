@echo off
chcp 65001 >nul
title 验证桌面截屏
cd /d "%~dp0" 2>nul
call "%~dp0_wsl_env.cmd"
if errorlevel 1 pause & exit /b 1

set "WIN_ROOT="
for /f "usebackq delims=" %%u in (`wsl -d %DISTRO% wslpath -w "%WSL_ROOT%" 2^>nul`) do set "WIN_ROOT=%%u"

echo === Windows 原生截屏验证 ===
echo  %WIN_ROOT%
echo.
if not exist "%WIN_ROOT%\scripts\windows\Verify-DesktopCapture.cmd" (
  echo 找不到脚本，请检查 WSL_ROOT=%WSL_ROOT%
  pause
  exit /b 1
)
call "%WIN_ROOT%\scripts\windows\Verify-DesktopCapture.cmd"
pause
