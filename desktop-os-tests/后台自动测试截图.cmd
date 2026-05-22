@echo off
chcp 65001 >nul
title 一键测试（快速不卡住）
cd /d "%~dp0" 2>nul
call "%~dp0_wsl_env.cmd"
if errorlevel 1 goto :fail

echo ========================================
echo  Memory Agent OS — 快速一键测试
echo ========================================
echo  约 1~3 分钟；先结束卡住的上次进程
echo.

wsl -d %DISTRO% bash -lc "cd '%WSL_ROOT%' && bash scripts/kill_stuck_test.sh"
wsl -d %DISTRO% bash -lc "cd '%WSL_ROOT%' && chmod +x scripts/fast_hr_test.py scripts/collect_test_result.sh && python3 scripts/fast_hr_test.py && bash scripts/collect_test_result.sh"
set RC=%ERRORLEVEL%

echo.
if %RC%==0 (echo [完成] 测试通过) else (echo [完成] 部分未通过，见上方或 report_hr.html)
for /f "usebackq delims=" %%p in (`wsl -d %DISTRO% wslpath -w "$(wsl -d %DISTRO% cat '%WSL_ROOT%/docs/test_runs/LATEST.txt')/report_hr.html" 2^>nul`) do start "" "%%p"
goto :end
:fail
echo 环境失败，请运行 0-诊断环境.cmd
:end
pause
