@echo off
chcp 65001 >nul
set GIT=C:\Program Files\Git\cmd\git.exe
set REPO=\\wsl.localhost\Ubuntu-22.04\home\zwq\AgentOSSystem
"%GIT%" config --global --add safe.directory "%REPO%"
"%GIT%" -C "%REPO%" config user.name "Zhang Weiqiang"
"%GIT%" -C "%REPO%" config user.email "126777810+kisaragiy@users.noreply.github.com"
"%GIT%" -C "%REPO%" add -A
"%GIT%" -C "%REPO%" commit -m "docs: professional public README, remove demo-only artifacts" 2>nul
"%GIT%" -C "%REPO%" push origin main
if errorlevel 1 (
  echo push failed
  exit /b 1
)
echo OK https://github.com/kisaragiy/Memory-Agent-OS
exit /b 0
