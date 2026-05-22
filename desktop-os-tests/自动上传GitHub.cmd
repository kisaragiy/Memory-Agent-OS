@echo off
chcp 65001 >nul
cd /d "%~dp0" 2>nul
call "%~dp0_wsl_env.cmd"
if errorlevel 1 pause & exit /b 1
echo 自动上传 GitHub（会校验远程 commit 是否一致）
wsl -d %DISTRO% bash -lc "chmod +x '%WSL_ROOT%/scripts/push_github_auto.sh' && '%WSL_ROOT%/scripts/push_github_auto.sh'"
set EC=%ERRORLEVEL%
echo.
powershell -NoProfile -Command "if (Test-Path '\\wsl.localhost\%DISTRO%\home\zwq\AgentOSSystem\scripts\push_github_auto.log') { Get-Content '\\wsl.localhost\%DISTRO%\home\zwq\AgentOSSystem\scripts\push_github_auto.log' -Tail 15 }"
if %EC%==0 (echo. & echo 成功: https://github.com/kisaragiy/Memory-Agent-OS) else (echo. & echo 未成功 — 请把 ~/.ssh/id_ed25519.pub 加到 GitHub SSH Keys 后重试)
pause
exit /b %EC%
