@echo off
chcp 65001 >nul
cd /d "%~dp0" 2>nul
call "%~dp0_wsl_env.cmd"
if errorlevel 1 (
  echo 环境失败，请先运行 0-诊断环境.cmd
  pause
  exit /b 1
)
start /MIN "AgentOS-Test" wsl -d %DISTRO% bash -lc "cd '%WSL_ROOT%' && chmod +x scripts/run_background_test.sh scripts/desktop_os_test_runner.sh && ./scripts/run_background_test.sh --detach --start-server"
echo 已在后台启动。完成后:
echo   wsl -d %DISTRO% cat "%WSL_ROOT%/docs/test_runs/LATEST.txt"
timeout /t 4 >nul
