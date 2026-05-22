@echo off
chcp 65001 >nul
title Phase5 自主循环测试
set "GOAL=看一下当前屏幕并描述界面"
echo === POST /api/autonomous/run ===
echo 目标: %GOAL%
echo 需先启动服务（新窗口启动服务.cmd）
echo.
curl -s -X POST http://127.0.0.1:8787/api/health >nul 2>&1
if errorlevel 1 (
  echo [错误] 服务未启动，请先运行「新窗口启动服务.cmd」
  pause
  exit /b 1
)
curl -s -X POST http://127.0.0.1:8787/api/autonomous/run ^
  -H "Content-Type: application/json" ^
  -d "{\"input\":\"%GOAL%\",\"mode\":\"developer\",\"user_confirmed\":true,\"max_autonomous_steps\":3}"
echo.
echo.
pause
