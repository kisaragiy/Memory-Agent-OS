@echo off
chcp 65001 >nul
title 健康检查
echo === GET /api/health ===
curl -s http://127.0.0.1:8787/api/health
echo.
echo.
echo === 桌面能力摘要 ===
curl -s http://127.0.0.1:8787/api/health 2>nul | findstr /i "desktop capture windows"
echo.
pause
