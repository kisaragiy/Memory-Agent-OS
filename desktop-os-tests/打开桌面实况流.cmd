@echo off
chcp 65001 >nul
title 打开桌面实况流
echo 正在打开浏览器 — 桌面实况（约 1.2 秒/帧）
echo 若黑屏请先运行「新窗口启动服务.cmd」
start "" "http://127.0.0.1:8787/api/desktop/stream"
timeout /t 2 >nul
