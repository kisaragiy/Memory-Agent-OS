@echo off
chcp 65001 >nul
cd /d "%~dp0" 2>nul
call "%~dp0_wsl_env.cmd"
if errorlevel 1 pause & exit /b 1
for /f "usebackq delims=" %%p in (`wsl -d %DISTRO% wslpath -w "$(wsl -d %DISTRO% cat '%WSL_ROOT%/docs/test_runs/LATEST.txt' 2^>nul)/report_hr.html" 2^>nul`) do (
  if exist "%%p" (
    start "" "%%p"
    echo 已打开: %%p
    goto :end
  )
)
echo 未找到报告，请先运行「后台自动测试截图.cmd」
:end
pause
