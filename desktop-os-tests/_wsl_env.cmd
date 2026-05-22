@echo off
REM 所有 desktop-os-tests\*.cmd 应先: call "%~dp0_wsl_env.cmd"
setlocal EnableExtensions EnableDelayedExpansion

set "DP0=%~dp0"
if "%DP0:~0,2%"=="\\" (
  pushd "%DP0%" 2>nul
  if errorlevel 1 (
    echo.
    echo [错误] 无法直接在网络路径 \\wsl.localhost\... 运行 .cmd
    echo   请双击「安装到桌面OS目录.cmd」复制到 桌面\OS  后再运行
    echo.
    endlocal
    exit /b 1
  )
  set "DP0=%CD%\"
) else (
  cd /d "%DP0%" 2>nul
)

set "DISTRO=Ubuntu-22.04"
if defined WSL_DISTRO_NAME set "DISTRO=%WSL_DISTRO_NAME%"

set "WSL_ROOT="
for /f "usebackq delims=" %%p in (`wsl -d !DISTRO! wslpath -u "!DP0!.." 2^>nul`) do set "WSL_ROOT=%%p"
if not defined WSL_ROOT set "WSL_ROOT=/home/zwq/AgentOSSystem"

wsl -d !DISTRO! test -d "!WSL_ROOT!" 2>nul
if errorlevel 1 (
  set "WSL_ROOT=/home/zwq/memory-chat"
  wsl -d !DISTRO! test -d "!WSL_ROOT!" 2>nul
  if errorlevel 1 (
    echo [错误] WSL 找不到项目。请编辑 _wsl_env.cmd 或检查仓库是否在 /home/zwq/AgentOSSystem
    if "!DP0:~0,2!"=="\\" popd 2>nul
    endlocal
    exit /b 1
  )
)

wsl -d !DISTRO! echo ok 1>nul 2>nul
if errorlevel 1 (
  echo [错误] 无法使用 WSL 发行版: !DISTRO!  请运行 wsl -l -v
  if "!DP0:~0,2!"=="\\" popd 2>nul
  endlocal
  exit /b 1
)

if "!DP0:~0,2!"=="\\" popd 2>nul
set "X_DISTRO=!DISTRO!"
set "X_ROOT=!WSL_ROOT!"
endlocal & set "DISTRO=%X_DISTRO%" & set "WSL_ROOT=%X_ROOT%"
exit /b 0
