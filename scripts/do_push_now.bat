@echo off
chcp 65001 >nul
set GIT=C:\Program Files\Git\cmd\git.exe
set REPO=\\wsl.localhost\Ubuntu-22.04\home\zwq\AgentOSSystem
set LOG=%REPO%\scripts\do_push_now.log
echo === push start %date% %time% === > "%LOG%"

"%GIT%" config --global --add safe.directory "%REPO%"
"%GIT%" -C "%REPO%" config user.name "Zhang Weiqiang"
"%GIT%" -C "%REPO%" config user.email "126777810+kisaragiy@users.noreply.github.com"
"%GIT%" -C "%REPO%" remote set-url origin https://github.com/kisaragiy/Memory-Agent-OS.git

echo remote >> "%LOG%"
"%GIT%" -C "%REPO%" remote -v >> "%LOG%" 2>&1
echo local >> "%LOG%"
"%GIT%" -C "%REPO%" log -1 --oneline >> "%LOG%" 2>&1

echo fetch >> "%LOG%"
"%GIT%" -C "%REPO%" fetch origin >> "%LOG%" 2>&1

echo pull unrelated >> "%LOG%"
"%GIT%" -C "%REPO%" pull origin main --allow-unrelated-histories --no-edit >> "%LOG%" 2>&1
if errorlevel 1 (
  echo pull failed, force push >> "%LOG%"
  "%GIT%" -C "%REPO%" push -u origin main --force-with-lease >> "%LOG%" 2>&1
) else (
  echo push after merge >> "%LOG%"
  "%GIT%" -C "%REPO%" push -u origin main >> "%LOG%" 2>&1
)

echo ls-remote >> "%LOG%"
"%GIT%" -C "%REPO%" ls-remote origin refs/heads/main >> "%LOG%" 2>&1

findstr /C:"77dc68e" "%LOG%" >nul && findstr /C:"85811d8" "%LOG%" >nul
if errorlevel 1 (
  echo SUCCESS >> "%LOG%"
  echo SUCCESS
  exit /b 0
)
"%GIT%" -C "%REPO%" ls-remote origin refs/heads/main | findstr /V "85811d8" >nul
if not errorlevel 1 (
  echo SUCCESS remote updated >> "%LOG%"
  echo SUCCESS
  exit /b 0
)
echo FAILED >> "%LOG%"
type "%LOG%"
exit /b 1
