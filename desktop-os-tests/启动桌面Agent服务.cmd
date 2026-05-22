@echo off
chcp 65001 >nul
title 启动桌面 Agent 服务
cd /d "%~dp0" 2>nul
call "%~dp0_wsl_env.cmd"
if errorlevel 1 pause & exit /b 1

echo === 启动 agent_service（WSL + 桌面模式）===
echo  项目: %WSL_ROOT%
echo  实况流: http://127.0.0.1:8787/api/desktop/stream
echo  Web UI: http://127.0.0.1:8787/app/
echo  关闭本窗口即停止服务
echo.
wsl -d %DISTRO% bash -lc "cd '%WSL_ROOT%' && GUARDED_UI_LIVE=1 ./scripts/run_desktop_wsl.sh"
pause
