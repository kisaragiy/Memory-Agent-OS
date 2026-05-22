# Full Windows desktop agent: see screen (vision) + guarded live automation.
# Requires: Python on Windows, Ollama with llama3.2-vision, optional pyautogui.

$here = $PSScriptRoot
& (Join-Path $here "run_agent_service.ps1") -Autonomous -Live -Desktop @args
