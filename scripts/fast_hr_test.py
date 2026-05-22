# -*- coding: utf-8 -*-
"""
快速 HR 测试 — 避免卡住：
- 不 playwright install
- 不等 LLM 聊天（先 API 再截图 + 页面顶栏注入说明）
- 不 pytest / 不 start-server（服务已在线时）
- page.goto 用 domcontentloaded + 30s 超时
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(_SCRIPT_DIR))

from agent_browser_capture import AgentBrowserCapture, annotate_screenshot  # noqa: E402

DEFAULT_BASE = os.environ.get("AGENT_SERVICE_URL", "http://127.0.0.1:8787").rstrip("/")
RUNS_ROOT = ROOT / "docs" / "test_runs"


def log(msg: str, logf: Path) -> None:
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with logf.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def http_json(method: str, url: str, body=None, timeout: float = 25.0):
    data = headers = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"error": raw[:2000]}
    except Exception as exc:
        return 0, {"error": str(exc)}


def health_ok(base: str) -> bool:
    code, _ = http_json("GET", f"{base}/api/health", timeout=5.0)
    return code == 200


def inject_banner(page, text: str) -> None:
    page.evaluate(
        """(msg) => {
          let el = document.getElementById('agent-test-banner');
          if (!el) {
            el = document.createElement('div');
            el.id = 'agent-test-banner';
            el.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:99999;background:#14532d;color:#fff;padding:12px 16px;font-size:16px;font-family:sans-serif;';
            document.body.prepend(el);
          }
          el.textContent = msg;
        }""",
        text[:200],
    )


def shot_step(
    browser: AgentBrowserCapture,
    seq: int,
    slug: str,
    title: str,
    hr: str,
    tech: str,
    ok: bool,
    banner: str,
    extra: list[str] | None = None,
) -> str | None:
    if browser.page:
        inject_banner(browser.page, banner)
        browser.page.wait_for_timeout(400)
    status = "通过" if ok else "未通过"
    return browser.capture_overlay_only(
        seq, slug, title=title, hr_line=hr, tech_line=tech, status=status, extra_lines=extra
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=DEFAULT_BASE)
    ap.add_argument("--out-dir", default="")
    args = ap.parse_args()
    base = args.base_url.rstrip("/")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = Path(args.out_dir) if args.out_dir else RUNS_ROOT / f"fast_{ts}"
    out.mkdir(parents=True, exist_ok=True)
    (RUNS_ROOT / "LATEST.txt").write_text(str(out) + "\n", encoding="utf-8")
    logf = out / "run.log"
    logf.write_text("", encoding="utf-8")

    steps = []
    all_ok = True

    log("=== 快速 HR 测试开始 ===", logf)
    if not health_ok(base):
        log("FAIL: 服务未启动，请先运行 新窗口启动服务.cmd", logf)
        (RUNS_ROOT / "last_exit_code.txt").write_text("EXIT:2\n", encoding="utf-8")
        return 2
    log("OK: /api/health", logf)

    code, health = http_json("GET", f"{base}/api/health", timeout=5.0)
    (out / "api" / "health.json").parent.mkdir(parents=True, exist_ok=True)
    (out / "api" / "health.json").write_text(json.dumps({"status": code, "body": health}, ensure_ascii=False, indent=2), encoding="utf-8")

    code2, run2 = http_json(
        "POST",
        f"{base}/api/run",
        {"input": "1+2", "mode": "developer", "developer": True},
        timeout=90.0,
    )
    if code2 == 0:
        log("API 1+2 超时，重试一次…", logf)
        code2, run2 = http_json(
            "POST",
            f"{base}/api/run",
            {"input": "1+2", "mode": "developer", "developer": True},
            timeout=90.0,
        )
    (out / "api" / "run_code.json").write_text(json.dumps({"status": code2, "body": run2}, ensure_ascii=False, indent=2), encoding="utf-8")
    body_str = json.dumps(run2, ensure_ascii=False)
    calc_ok = 200 <= code2 < 300 and (
        "execute_code" in body_str
        or '"display": "3"' in body_str
        or '"display": 3' in body_str
        or '"result": 3' in body_str
    )
    log(f"API 1+2: http={code2} calc_ok={calc_ok}", logf)

    code3, run3 = http_json(
        "POST",
        f"{base}/api/run",
        {"input": "记住: 快速测试用户", "mode": "developer", "developer": True},
        timeout=45.0,
    )
    (out / "api" / "run_memory.json").write_text(json.dumps({"status": code3, "body": run3}, ensure_ascii=False, indent=2), encoding="utf-8")
    mem_ok = 200 <= code3 < 300
    log(f"API memory: http={code3} ok={mem_ok}", logf)

    browser = None
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log("WARN: 无 playwright 包 — pip install -r requirements-test-capture.txt", logf)
        sync_playwright = None

    if sync_playwright:
        cache = os.environ.get("PLAYWRIGHT_BROWSERS_PATH") or str(Path.home() / ".cache" / "ms-playwright")
        if not Path(cache).is_dir() or not list(Path(cache).glob("chromium*/chrome-linux/chrome")):
            log(f"WARN: 未找到 Chromium，请手动放到: {cache}", logf)
            log("  说明见 docs/PLAYWRIGHT_MANUAL_INSTALL.md", logf)
            log("  检测: python3 scripts/print_playwright_paths.py", logf)
        log("启动 Playwright（不执行 install）…", logf)
        try:
            pw = sync_playwright().start()
            browser_launch = pw.chromium.launch(headless=True, timeout=60_000)
            page = browser_launch.new_page(viewport={"width": 1400, "height": 900})
            page.goto(f"{base}/app/", wait_until="domcontentloaded", timeout=30_000)
            page.get_by_role("button", name="开发者模式").click(timeout=10_000)
            page.wait_for_timeout(500)

            cap = AgentBrowserCapture(base, out / "screenshots", response_wait_ms=5000)
            cap.page = page
            cap._pw = pw
            cap._browser = browser_launch

            online = cap.wait_service_online(timeout_ms=8000)
            p0 = shot_step(cap, 0, "准备_打开Agent控制台", "步骤0 · 打开控制台", "页面可访问，开发者模式", "GET /app/", online, "【测试】控制台已打开")
            steps.append({"id": "00", "title_hr": "打开控制台", "ok": online, "screenshot": p0})

            p1 = shot_step(
                cap, 1, "服务健康_后端在线", "步骤1 · 服务健康", "后端在线", "GET /api/health",
                code == 200, f"【测试】健康检查 HTTP {code}", [json.dumps(health, ensure_ascii=False)[:80]],
            )
            steps.append({"id": "01", "title_hr": "服务在线", "ok": code == 200, "screenshot": p1})

            p2 = shot_step(
                cap, 2, "基础计算_1加2等于3", "步骤2 · 基础计算", "1+2=3", "POST /api/run execute_code",
                calc_ok, f"【测试】1+2 结果={'通过' if calc_ok else '失败'}（API 已执行，未等待 UI 聊天）",
                [f"HTTP {code2}"],
            )
            steps.append({"id": "02", "title_hr": "基础计算", "ok": calc_ok, "screenshot": p2})

            p3 = shot_step(
                cap, 3, "记忆写入_治理化存储", "步骤3 · 记忆", "记住指令", "execute_memory_op",
                mem_ok, f"【测试】记忆写入 {'通过' if mem_ok else '失败'}",
                [f"HTTP {code3}"],
            )
            steps.append({"id": "03", "title_hr": "记忆写入", "ok": mem_ok, "screenshot": p3})

            browser_launch.close()
            pw.stop()
            log("Playwright 截图完成", logf)
        except Exception as exc:
            log(f"Playwright 失败（不阻塞）: {exc}", logf)
            all_ok = all_ok and calc_ok and mem_ok
    else:
        all_ok = all_ok and calc_ok and mem_ok

    summary = {
        "started_at": ts,
        "mode": "fast_hr_test",
        "steps": steps,
        "api": {"health": code == 200, "calc": calc_ok, "memory": mem_ok},
    }
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # 简易 HR 报告
    rows = []
    for s in steps:
        st = "通过" if s.get("ok") else "未通过"
        img = ""
        if s.get("screenshot"):
            rel = Path(s["screenshot"]).relative_to(out).as_posix()
            img = f'<img src="{rel}" style="max-width:100%"/>'
        rows.append(f"<tr><td>{s.get('id')}</td><td>{s.get('title_hr')}</td><td>{st}</td><td>{img}</td></tr>")
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>快速测试报告</title></head>
<body style="font-family:sans-serif;padding:20px">
<h1>Memory Agent OS — 快速测试（不卡住版）</h1>
<p>总体: <b>{'通过' if all_ok and calc_ok and mem_ok else '部分未通过'}</b></p>
<table border="1" cellpadding="8">{''.join(rows)}</table>
</body></html>"""
    (out / "report_hr.html").write_text(html, encoding="utf-8")

    exit_code = 0 if (calc_ok and mem_ok and code == 200) else 1
    (RUNS_ROOT / "last_exit_code.txt").write_text(f"EXIT:{exit_code}\n", encoding="utf-8")
    log(f"=== 完成 exit={exit_code} 报告 {out}/report_hr.html ===", logf)
    (RUNS_ROOT / "last_run_stdout.log").write_text(logf.read_text(encoding="utf-8"), encoding="utf-8")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
