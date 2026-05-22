@echo off
chcp 65001 >nul
cd /d "%~dp0" 2>nul
call "%~dp0_wsl_env.cmd"
if errorlevel 1 pause & exit /b 1
echo 推送到 https://github.com/kisaragiy/Memory-Agent-OS
echo 不含简历 PDF；需已登录 GitHub（gh auth 或 HTTPS 凭据）
wsl -d %DISTRO% bash -lc "chmod +x '%WSL_ROOT%/scripts/push_github.sh' && '%WSL_ROOT%/scripts/push_github.sh'"
echo.
if exist "%WSL_ROOT%\scripts\push_github_result.txt" type "\\wsl.localhost\%DISTRO%\home\zwq\AgentOSSystem\scripts\push_github_result.txt"
pause
