@echo off
chcp 65001 >nul
title 诊断 WSL / 项目路径
cd /d "%~dp0" 2>nul
call "%~dp0_wsl_env.cmd"
if errorlevel 1 goto :end

echo ========================================
echo  环境诊断
echo ========================================
echo  WSL 发行版: %DISTRO%
echo  项目目录:   %WSL_ROOT%
echo.

echo [1] WSL 与目录...
wsl -d %DISTRO% bash -lc "uname -a; test -d '%WSL_ROOT%' && echo OK: 项目存在 || echo FAIL: 项目不存在"
echo.

echo [2] Python...
wsl -d %DISTRO% bash -lc "cd '%WSL_ROOT%' && (test -f .venv/bin/activate && . .venv/bin/activate; python3 --version; which python3)"
echo.

echo [3] 前端是否已构建...
wsl -d %DISTRO% bash -lc "test -f '%WSL_ROOT%/web/frontend/dist/index.html' && echo OK: dist 存在 || echo 缺少 dist，需运行 start_production.sh 构建"
echo.

echo [4] 服务健康 (8787)...
curl -s -m 3 http://127.0.0.1:8787/api/health 2>nul || echo 服务未启动（一键测试会自动 --start-server）
echo.

echo [5] Playwright...
wsl -d %DISTRO% bash -lc "cd '%WSL_ROOT%' && python3 -c 'import playwright; print(playwright.__version__)' 2>/dev/null || echo 未安装，一键测试会自动安装"
echo.
echo 若以上正常，请运行「后台自动测试截图.cmd」
:end
pause
