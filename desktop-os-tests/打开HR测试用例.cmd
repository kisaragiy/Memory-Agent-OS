@echo off
chcp 65001 >nul
set "DOC=%~dp0..\docs\HR_TEST_CASES.md"
if not exist "%DOC%" (
  echo 未找到: %DOC%
  pause
  exit /b 1
)
start "" "%DOC%"
echo 已打开 HR 测试用例文档
echo 录屏前请先运行: 新窗口启动服务.cmd
pause
