@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_agent_service.ps1" %*
