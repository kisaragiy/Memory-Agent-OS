@echo off
chcp 65001 >nul
cd /d "%~dp0" 2>nul
call "%~dp0_wsl_env.cmd"
if errorlevel 1 pause & exit /b 1
start "Memory Agent OS" wsl -d %DISTRO% bash -lc "cd '%WSL_ROOT%' && GUARDED_UI_LIVE=1 ./scripts/run_desktop_wsl.sh"
echo 已在新窗口启动服务: http://127.0.0.1:8787/app/
