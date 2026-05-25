@echo off
chcp 65001 >nul
set GIT=C:\Program Files\Git\cmd\git.exe
set REPO=\\wsl.localhost\Ubuntu-22.04\home\zwq\AgentOSSystem
set DESC=基于 Python、FastAPI 与 React 的单内核 LLM Agent Runtime，集成治理化记忆、虚拟世界状态机与 Phase5 自主闭环，提供可观测执行 trace 与开发者控制台。

"%GIT%" config --global --add safe.directory "%REPO%"
"%GIT%" -C "%REPO%" config user.name "Zhang Weiqiang"
"%GIT%" -C "%REPO%" config user.email "126777810+kisaragiy@users.noreply.github.com"

echo Removing local-only paths from git index...
for %%P in (
  "desktop-os-tests"
  "PORTFOLIO.md"
  "docs/GITHUB_UPLOAD.md"
  "docs/RESUME_CONTENT.md"
  "docs/PLAYWRIGHT_MANUAL_INSTALL.md"
  "docs/resume_verify.txt"
  "requirements-test-capture.txt"
  "requirements-docs.txt"
  "scripts/push_github.sh"
  "scripts/push_github_auto.sh"
  "scripts/push_github_result.txt"
  "scripts/push_like_movie_project.ps1"
  "scripts/do_push_now.bat"
  "scripts/do_push_now.ps1"
  "scripts/do_push_now.log"
  "scripts/clean_github_history.bat"
  "scripts/clean_github_history.sh"
  "scripts/publish_public_repo.bat"
  "scripts/cleanup_public_and_push.bat"
  "scripts/setup_ssh_and_push.sh"
  "scripts/do_git_commit.sh"
  "scripts/_run_exact.sh"
  "scripts/generate_resume_pdf.py"
  "scripts/build_resume.bat"
  "scripts/check_resume_and_git.sh"
  "scripts/fast_hr_test.py"
  "scripts/background_test_capture.py"
  "scripts/agent_browser_capture.py"
  "scripts/collect_test_result.sh"
  "scripts/quick_test_for_agent.sh"
  "scripts/desktop_os_test_runner.sh"
  "scripts/run_background_test.sh"
  "scripts/kill_stuck_test.sh"
  "scripts/print_playwright_paths.py"
  "scripts/build_portfolio_docs.sh"
  "scripts/generate_portfolio_docs.py"
  "scripts/push_github_auto.log"
  "scripts/clean_history.log"
) do (
  "%GIT%" -C "%REPO%" rm -rf --cached --ignore-unmatch "%%~P" 2>nul
)

"%GIT%" -C "%REPO%" add -A
"%GIT%" -C "%REPO%" commit -m "chore: public repo polish — remove local-only tooling and docs"
if errorlevel 1 (
  echo no commit needed or commit failed
)

"%GIT%" -C "%REPO%" push origin main
if errorlevel 1 exit /b 1

where gh >nul 2>&1
if not errorlevel 1 (
  gh repo edit kisaragiy/Memory-Agent-OS --description "%DESC%"
  echo GitHub description updated.
) else (
  echo Install GitHub CLI and run: gh repo edit kisaragiy/Memory-Agent-OS --description "..."
)

echo OK https://github.com/kisaragiy/Memory-Agent-OS
exit /b 0
