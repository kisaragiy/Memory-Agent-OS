@echo off
chcp 65001 >nul
set GIT=C:\Program Files\Git\cmd\git.exe
set REPO=\\wsl.localhost\Ubuntu-22.04\home\zwq\AgentOSSystem
set LOG=%REPO%\scripts\clean_history.log
echo === clean history %date% %time% === > "%LOG%"

"%GIT%" config --global --add safe.directory "%REPO%"
"%GIT%" -C "%REPO%" config user.name "Zhang Weiqiang"
"%GIT%" -C "%REPO%" config user.email "126777810+kisaragiy@users.noreply.github.com"

echo Remove junk from index >> "%LOG%"
"%GIT%" -C "%REPO%" rm -rf --cached --ignore-unmatch "File: core/runtime/agent_os_runtime.py" >> "%LOG%" 2>&1
"%GIT%" -C "%REPO%" rm -rf --cached --ignore-unmatch "File: core/runtime/execution_engine.py" >> "%LOG%" 2>&1
"%GIT%" -C "%REPO%" rm -rf --cached --ignore-unmatch "File: core/runtime/observability.py" >> "%LOG%" 2>&1
"%GIT%" -C "%REPO%" rm -rf --cached --ignore-unmatch "Output capability registry list (debug)" >> "%LOG%" 2>&1

echo checkout orphan >> "%LOG%"
"%GIT%" -C "%REPO%" checkout --orphan portfolio-clean >> "%LOG%" 2>&1
"%GIT%" -C "%REPO%" add -A >> "%LOG%" 2>&1
"%GIT%" -C "%REPO%" commit -m "feat: Memory Agent OS — single-kernel LLM agent runtime" >> "%LOG%" 2>&1
if errorlevel 1 (
  echo commit failed >> "%LOG%"
  type "%LOG%"
  exit /b 1
)

"%GIT%" -C "%REPO%" branch -M main >> "%LOG%" 2>&1
echo push >> "%LOG%"
"%GIT%" -C "%REPO%" push -u origin main --force >> "%LOG%" 2>&1
if errorlevel 1 (
  echo push failed >> "%LOG%"
  type "%LOG%"
  exit /b 1
)

"%GIT%" -C "%REPO%" log -1 --oneline >> "%LOG%" 2>&1
echo SUCCESS >> "%LOG%"
echo SUCCESS
type "%LOG%"
exit /b 0
