@echo off
chcp 65001 >nul
title 一键全套测试
cd /d "%~dp0" 2>nul
call "%~dp0_wsl_env.cmd"
if errorlevel 1 pause & exit /b 1

echo ========================================
echo  Memory Agent OS — 一键全套测试
echo  项目: %WSL_ROOT%
echo ========================================
echo.
echo [1/3] WSL 桌面截屏验证...
wsl -d %DISTRO% bash -lc "cd '%WSL_ROOT%' && AGENT_WINDOWS_DESKTOP=1 python3 scripts/verify_desktop_capture.py"
if errorlevel 1 goto :fail
echo.
echo [2/3] 健康检查...
curl -s -m 5 http://127.0.0.1:8787/api/health 2>nul
if errorlevel 1 (
  echo  服务未运行 — 请双击「新窗口启动服务.cmd」
) else (
  echo  服务在线 OK
)
echo.
echo [3/3] 打开浏览器...
start "" "http://127.0.0.1:8787/app/"
goto :end
:fail
echo 测试未全部通过。
:end
pause
