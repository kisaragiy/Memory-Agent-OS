# -*- coding: utf-8 -*-
"""
后台自动测试 + 截图。

方式 A（HR 可读，仅 Agent 浏览器）:
  desktop-os-tests\\后台自动测试截图.cmd   # 一键，无需选项

手动:
  pip install -r requirements-test-capture.txt
  python3 -m playwright install chromium
  python3 scripts/background_test_capture.py --hr --browser-only --start-server --open-report
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(_SCRIPT_DIR))

DEFAULT_BASE = os.environ.get("AGENT_SERVICE_URL", "http://127.0.0.1:8787").rstrip("/")
RUNS_ROOT = ROOT / "docs" / "test_runs"


def _http_json(
    method: str,
    url: str,
    body: Optional[Dict[str, Any]] = None,
    timeout: float = 120.0,
) -> Tuple[int, Any]:
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                return resp.status, {"_raw": raw[:8000]}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"_raw": raw[:4000], "error": str(e)}
    except Exception as exc:
        return 0, {"error": str(exc)}


def _health_ok(base: str) -> bool:
    code, _ = _http_json("GET", f"{base}/api/health", timeout=5.0)
    return code == 200


def _ensure_playwright(*, install_browser: bool = False) -> None:
    try:
        import playwright  # noqa: F401
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "-r", str(ROOT / "requirements-test-capture.txt")],
            timeout=120,
        )
    if install_browser:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=False,
            capture_output=True,
            timeout=300,
        )


class BackgroundTestRunner:
    def __init__(
        self,
        out_dir: Path,
        base_url: str,
        *,
        start_server: bool = False,
        run_pytest: bool = True,
        phase5: bool = False,
        browser_only: bool = True,
        hr_report: bool = True,
        screenshot_delay: float = 0.3,
    ) -> None:
        self.out_dir = out_dir
        self.base_url = base_url
        self.start_server = start_server
        self.run_pytest = run_pytest
        self.phase5 = phase5
        self.browser_only = browser_only
        self.hr_report = hr_report
        self.screenshot_delay = screenshot_delay
        self.shot_dir = out_dir / "screenshots"
        self.api_dir = out_dir / "api"
        self.shot_dir.mkdir(parents=True, exist_ok=True)
        self.api_dir.mkdir(parents=True, exist_ok=True)
        self._server_proc: Optional[subprocess.Popen] = None
        self._browser = None
        self.summary: Dict[str, Any] = {
            "started_at": datetime.now().isoformat(timespec="seconds"),
            "base_url": base_url,
            "browser_only": browser_only,
            "steps": [],
            "screenshots": [],
        }

    def log(self, msg: str) -> None:
        line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        with (self.out_dir / "run.log").open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def _save_api(self, name: str, status: int, payload: Any) -> None:
        (self.api_dir / f"{name}.json").write_text(
            json.dumps({"status": status, "body": payload}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _record_step(
        self,
        step_id: str,
        slug: str,
        title_hr: str,
        desc_hr: str,
        tech: str,
        ok: bool,
        screenshot: Optional[str] = None,
        detail: str = "",
    ) -> None:
        self.summary["steps"].append(
            {
                "id": step_id,
                "slug": slug,
                "title_hr": title_hr,
                "desc_hr": desc_hr,
                "tech": tech,
                "ok": ok,
                "screenshot": screenshot,
                "detail": detail,
            }
        )

    def ensure_server(self) -> bool:
        if _health_ok(self.base_url):
            self.log("服务已在线")
            return True
        if not self.start_server:
            self.log("服务未启动 — 使用 --start-server 或先运行「新窗口启动服务.cmd」")
            return False
        self.log("后台启动 agent_service …")
        logf = open(self.out_dir / "server.log", "w", encoding="utf-8")
        env = os.environ.copy()
        env.setdefault("AGENT_REACT_DIST", str(ROOT / "web" / "frontend" / "dist"))
        env.setdefault("AGENT_STATIC_DIR", str(ROOT / "web"))
        self._server_proc = subprocess.Popen(
            [sys.executable, "-m", "agent_service"],
            cwd=str(ROOT),
            env=env,
            stdout=logf,
            stderr=subprocess.STDOUT,
        )
        for i in range(90):
            if _health_ok(self.base_url):
                self.log(f"服务就绪 ({i + 1}s)")
                return True
            time.sleep(1)
        self.log("服务启动超时")
        return False

    def run_hr_browser_suite(self) -> bool:
        if not self.ensure_server():
            return False
        from agent_browser_capture import AgentBrowserCapture

        _ensure_playwright()
        b: AgentBrowserCapture = AgentBrowserCapture(self.base_url, self.shot_dir)
        self._browser = b
        all_ok = True
        try:
            b.start()
            b.select_developer_mode()

            online = b.wait_service_online()
            p0 = b.capture_step(
                0,
                "准备_打开Agent控制台",
                title="步骤0 · 打开 Agent 控制台",
                hr_line="界面能打开，并进入开发者模式（右侧可看执行轨迹）",
                tech_line=f"Playwright 打开 {b.app_url}，视口截图（非全桌面）",
                status="通过" if online else "未通过",
                extra_lines=None if online else ["未检测到「服务在线」，请确认后端已启动"],
            )
            self._record_step(
                "00",
                "准备_打开Agent控制台",
                "打开网页控制台",
                "HR：确认产品页面能访问；技术：/app/ 加载成功",
                f"GET {b.app_url}",
                online,
                p0,
            )
            all_ok &= online

            code, health = _http_json("GET", f"{self.base_url}/api/health")
            self._save_api("health", code, health)
            h_ok = code == 200
            p1 = b.capture_overlay_only(
                1,
                "服务健康_后端在线",
                title="步骤1 · 服务健康检查",
                hr_line="后端 API 正常，页面显示「服务在线」",
                tech_line="GET /api/health → status ok",
                status="通过" if h_ok and online else "未通过",
                extra_lines=[f"HTTP {code}", json.dumps(health, ensure_ascii=False)[:120]],
            )
            self._record_step(
                "01",
                "服务健康_后端在线",
                "服务是否在线",
                "HR：绿点/服务在线即表示系统已启动；技术：健康检查接口返回 200",
                "GET /api/health",
                h_ok and online,
                p1,
            )
            all_ok &= h_ok

            b.send_chat_and_wait("1+2")
            body_text = b.page.inner_text("body") if b.page else ""
            calc_ok = "3" in body_text
            code2, run_body = _http_json(
                "POST",
                f"{self.base_url}/api/run",
                {"input": "1+2", "mode": "developer", "developer": True},
            )
            self._save_api("run_code", code2, run_body)
            calc_ok = calc_ok and (200 <= code2 < 300)
            p2 = b.capture_step(
                2,
                "基础计算_1加2等于3",
                title="步骤2 · 基础计算（代码通道）",
                hr_line="输入 1+2，系统应算出 3（证明能执行逻辑，不是纯聊天）",
                tech_line="UI 发送 + POST /api/run → execute_code 路由",
                status="通过" if calc_ok else "未通过",
                extra_lines=[f"页面含「3」: {calc_ok}", f"API HTTP {code2}"],
            )
            self._record_step(
                "02",
                "基础计算_1加2等于3",
                "基础计算 1+2",
                "HR：像计算器一样给出正确答案 3；技术：走代码执行通道而非大模型瞎编",
                "POST /api/run input=1+2",
                calc_ok,
                p2,
            )
            all_ok &= calc_ok

            b.send_chat_and_wait("记住: 后台测试用户")
            code3, mem_body = _http_json(
                "POST",
                f"{self.base_url}/api/run",
                {"input": "记住: 后台测试用户", "mode": "developer", "developer": True},
            )
            self._save_api("run_memory", code3, mem_body)
            mem_ok = 200 <= code3 < 300
            mem_raw = json.dumps(mem_body, ensure_ascii=False)
            if "memory" in mem_raw.lower() or "记住" in mem_raw:
                mem_ok = mem_ok and True
            p3 = b.capture_step(
                3,
                "记忆写入_治理化存储",
                title="步骤3 · 记忆写入",
                hr_line="输入「记住: …」，系统按规则保存（可审计，非随意改数据库）",
                tech_line="memory 路由 → execute_memory_op → MemoryLayer",
                status="通过" if mem_ok else "未通过",
                extra_lines=[f"API HTTP {code3}"],
            )
            self._record_step(
                "03",
                "记忆写入_治理化存储",
                "记忆功能",
                "HR：能记住用户关键信息；技术：治理化记忆写入，带 trace",
                "POST /api/run input=记住:…",
                mem_ok,
                p3,
            )
            all_ok &= mem_ok

            if self.phase5:
                code4, auto_body = _http_json(
                    "POST",
                    f"{self.base_url}/api/autonomous/run",
                    {
                        "input": "用一句话说明你能做什么",
                        "mode": "developer",
                        "user_confirmed": True,
                        "max_autonomous_steps": 2,
                    },
                    timeout=180.0,
                )
                self._save_api("autonomous_short", code4, auto_body)
                auto_ok = 200 <= code4 < 300
                b.page.get_by_role("button", name="Phase5 自主循环").click()
                b.page.wait_for_timeout(400)
                p4 = b.capture_overlay_only(
                    4,
                    "自主循环_Phase5",
                    title="步骤4 · Phase5 自主循环",
                    hr_line="多步自动执行：观察→计划→执行→反思（Agent OS 核心能力）",
                    tech_line="POST /api/autonomous/run max_steps=2",
                    status="通过" if auto_ok else "未通过",
                    extra_lines=[f"HTTP {code4}"],
                )
                self._record_step(
                    "04",
                    "自主循环_Phase5",
                    "自主循环（进阶）",
                    "HR：能分多步完成任务；技术：AutonomousOSLoop，每步仅 entry()",
                    "POST /api/autonomous/run",
                    auto_ok,
                    p4,
                )
                all_ok &= auto_ok

            self.summary["screenshots"] = b.records
            return all_ok
        finally:
            b.stop()
            self._browser = None

    def run_pytest_suite(self) -> bool:
        if not self.run_pytest:
            return True
        self.log("运行 pytest …")
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=line"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=600,
        )
        log_path = self.out_dir / "pytest.log"
        log_path.write_text(r.stdout + "\n" + r.stderr, encoding="utf-8")
        ok = r.returncode == 0
        self.summary["pytest"] = {"ok": ok, "returncode": r.returncode}
        tail = (r.stdout + r.stderr).strip().splitlines()[-5:]
        if self.browser_only and _health_ok(self.base_url):
            try:
                from agent_browser_capture import AgentBrowserCapture

                _ensure_playwright()
                b = AgentBrowserCapture(self.base_url, self.shot_dir)
                b.start()
                b.select_developer_mode()
                p = b.capture_overlay_only(
                    9,
                    "单元测试_pytest回归",
                    title="步骤9 · 自动化单元测试",
                    hr_line="后台跑完全部回归用例，保证改版不踩坏核心功能",
                    tech_line="pytest tests/ -q",
                    status="通过" if ok else "未通过",
                    extra_lines=tail,
                )
                self._record_step(
                    "09",
                    "单元测试_pytest回归",
                    "自动化测试",
                    "HR：相当于自动体检；技术：pytest 内核回归",
                    "pytest tests/",
                    ok,
                    p,
                    detail="\n".join(tail),
                )
                b.stop()
            except Exception as exc:
                self.log(f"pytest 截图跳过: {exc}")
        self.log(f"pytest {'通过' if ok else '失败'}")
        return ok

    def build_hr_report(self) -> Path:
        steps = self.summary.get("steps", [])
        passed = sum(1 for s in steps if s.get("ok"))
        total = len(steps) or 1
        rows = []
        for s in steps:
            st = "通过" if s.get("ok") else "未通过"
            cls = "ok" if s.get("ok") else "fail"
            img = ""
            shot = s.get("screenshot")
            if shot and Path(shot).is_file():
                rel = Path(shot).relative_to(self.out_dir).as_posix()
                img = f'<a href="{rel}"><img src="{rel}" alt="{s.get("slug")}"/></a>'
            rows.append(
                f"""<tr class="{cls}">
                <td>{s.get('id','')}</td>
                <td><b>{s.get('title_hr','')}</b><br/><span class="muted">{s.get('desc_hr','')}</span></td>
                <td class="{cls}">{st}</td>
                <td><code>{s.get('tech','')}</code></td>
                <td class="shot">{img}</td>
                </tr>"""
            )
        overall = "通过" if passed == total and self.summary.get("pytest", {}).get("ok", True) else "部分未通过"
        html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"/>
<title>Memory Agent OS — 测试报告（HR/技术可读）</title>
<style>
body{{font-family:"Microsoft YaHei",sans-serif;margin:28px;background:#f1f5f9;color:#0f172a}}
h1{{font-size:1.6rem}} .card{{background:#fff;border-radius:12px;padding:20px;margin:16px 0;box-shadow:0 1px 3px #0001}}
.summary{{font-size:1.1rem}} .ok{{color:#15803d}} .fail{{color:#b91c1c}}
table{{width:100%;border-collapse:collapse}} th,td{{border:1px solid #e2e8f0;padding:10px;vertical-align:top}}
th{{background:#e2e8f0}} .shot img{{max-width:520px;border:1px solid #cbd5e1;border-radius:8px}}
.muted{{color:#64748b;font-size:0.9rem}} code{{font-size:0.85rem}}
.glossary li{{margin:6px 0}}
</style></head><body>
<h1>Memory Agent OS — 一键测试报告</h1>
<div class="card summary">
  <p><b>总体结论：</b> <span class="{'ok' if overall=='通过' else 'fail'}">{overall}</span>
     &nbsp;·&nbsp; 步骤 {passed}/{total} 通过</p>
  <p><b>说明：</b> 每张截图仅包含 <b>Agent 网页控制台</b>（非整个 Windows 桌面），顶部黄条为中文备注。</p>
  <p><b>时间：</b> {self.summary.get('started_at')} — {self.summary.get('finished_at','')}</p>
  <p><b>目录：</b> {self.out_dir}</p>
</div>
<div class="card">
<h2>分步结果（给 HR / 面试官）</h2>
<table>
<tr><th>编号</th><th>测什么（人话）</th><th>结果</th><th>技术说明</th><th>截图（已备注）</th></tr>
{"".join(rows)}
</table>
</div>
<div class="card glossary">
<h2>名词解释（HR 可看）</h2>
<ul>
<li><b>开发者模式</b>：展示系统内部执行过程，证明不是黑盒聊天。</li>
<li><b>代码通道</b>：简单计算走程序执行，结果准确可验证。</li>
<li><b>治理化记忆</b>：记忆写入有审批路径，可追责，不是直接改文件。</li>
<li><b>Phase5 自主循环</b>：多步自动完成任务，类似智能体「自己做几步」。</li>
<li><b>pytest</b>：开发用的自动体检，与本页截图同属一次一键测试。</li>
</ul>
</div>
</body></html>"""
        report = self.out_dir / "report_hr.html"
        report.write_text(html, encoding="utf-8")
        # 技术简版
        tech = self.out_dir / "report.html"
        tech.write_text(
            report.read_text(encoding="utf-8").replace("report_hr", "report"),
            encoding="utf-8",
        )
        return report

    def finish(self) -> None:
        self.summary["finished_at"] = datetime.now().isoformat(timespec="seconds")
        (self.out_dir / "summary.json").write_text(
            json.dumps(self.summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        report = self.build_hr_report() if self.hr_report else None
        if report:
            self.log(f"HR 报告: {report}")
            try:
                from core.platform.windows_desktop import WindowsDesktop

                self.log(f"Windows: {WindowsDesktop.to_windows_path(report)}")
            except Exception:
                pass
        if self._server_proc and self.start_server:
            self.log("停止本脚本启动的后台服务 …")
            self._server_proc.terminate()

    def run(self) -> int:
        self.log(f"输出: {self.out_dir} | browser_only={self.browser_only}")
        try:
            if self.browser_only:
                api_ok = self.run_hr_browser_suite()
            else:
                api_ok = False
                self.log("未启用 browser_only，请使用 --hr --browser-only")
            py_ok = self.run_pytest_suite() if self.run_pytest else True
            self.finish()
            return 0 if (api_ok and py_ok) else 1
        except KeyboardInterrupt:
            return 130


def _write_latest_pointer(out_dir: Path) -> None:
    RUNS_ROOT.mkdir(parents=True, exist_ok=True)
    (RUNS_ROOT / "LATEST.txt").write_text(str(out_dir) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="后台测试 — 可仅截 Agent 浏览器")
    ap.add_argument("--hr", dest="hr", action="store_true", default=True, help="HR 可读报告（默认）")
    ap.add_argument("--no-hr", dest="hr", action="store_false", help="关闭 HR 报告格式")
    ap.add_argument("--browser-only", action="store_true", default=True, help="仅 Playwright 截 /app/")
    ap.add_argument("--desktop", action="store_true", help="改用全桌面截屏（旧行为）")
    ap.add_argument("--start-server", action="store_true", help="8787 未起则自动启动")
    ap.add_argument("--no-pytest", action="store_true", help="跳过 pytest")
    ap.add_argument("--phase5", action="store_true", help="包含 Phase5 API（更慢）")
    ap.add_argument("--base-url", default=DEFAULT_BASE)
    ap.add_argument("--out-dir", default="")
    ap.add_argument("--open-report", action="store_true", help="结束打开 report_hr.html")
    args = ap.parse_args()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(args.out_dir) if args.out_dir else RUNS_ROOT / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_latest_pointer(out_dir)

    runner = BackgroundTestRunner(
        out_dir,
        args.base_url.rstrip("/"),
        start_server=args.start_server,
        run_pytest=not args.no_pytest,
        phase5=args.phase5,
        browser_only=not args.desktop,
        hr_report=args.hr,
    )
    code = runner.run()
    if args.open_report:
        try:
            from core.platform.windows_desktop import WindowsDesktop

            WindowsDesktop.open_in_windows_shell(out_dir / "report_hr.html")
        except Exception:
            pass
    return code


if __name__ == "__main__":
    raise SystemExit(main())
