@echo off
chcp 65001 >nul
title WSL 验证桌面截屏
cd /d "%~dp0" 2>nul
call "%~dp0_wsl_env.cmd"
if errorlevel 1 pause & exit /b 1
echo === WSL -^> Windows 桌面截屏 ===
echo  项目: %WSL_ROOT%
echo.
wsl -d %DISTRO% bash -lc "cd '%WSL_ROOT%' && AGENT_WINDOWS_DESKTOP=1 python3 scripts/verify_desktop_capture.py"
echo.
pause
