@echo off
chcp 65001 >nul
title 安装到桌面 OS 目录
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0安装到桌面OS目录.ps1"
pause
