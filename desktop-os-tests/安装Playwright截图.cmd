@echo off
chcp 65001 >nul
title Playwright 路径说明 / 在线安装
cd /d "%~dp0" 2>nul
call "%~dp0_wsl_env.cmd"
if errorlevel 1 pause & exit /b 1

echo ========================================
echo  Playwright Chromium 安装
echo ========================================
echo.
echo 【手动放置路径 - WSL】
echo   /home/zwq/.cache/ms-playwright/
echo   详见项目: docs\PLAYWRIGHT_MANUAL_INSTALL.md
echo.
echo 正在检测当前状态...
wsl -d %DISTRO% bash -lc "cd '%WSL_ROOT%' && pip install -q -r requirements-test-capture.txt 2>/dev/null; python3 scripts/print_playwright_paths.py"
echo.
set /p CHOICE="在线自动下载 chromium? (Y/N，国内慢选 N 后手动拷贝): "
if /i "%CHOICE%"=="Y" (
  wsl -d %DISTRO% bash -lc "cd '%WSL_ROOT%' && python3 -m playwright install chromium"
) else (
  echo 请按 PLAYWRIGHT_MANUAL_INSTALL.md 放好后再运行「后台自动测试截图.cmd」
)
pause
