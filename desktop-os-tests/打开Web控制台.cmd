@echo off
chcp 65001 >nul
title 打开 Web 控制台
echo 请切换到「开发者模式」，右侧可见「桌面实况」面板
start "" "http://127.0.0.1:8787/app/"
