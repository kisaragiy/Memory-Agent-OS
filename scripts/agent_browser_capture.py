# -*- coding: utf-8 -*-
"""Playwright — 仅截取 Memory Agent OS 网页控制台（/app/），并叠加中文备注。"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont


def _font(size: int = 18) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for p in (
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
    ):
        if Path(p).is_file():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def annotate_screenshot(
    src: Path,
    dest: Path,
    *,
    title: str,
    hr_line: str,
    tech_line: str,
    status: str,
    extra_lines: Optional[List[str]] = None,
) -> Path:
    """在截图顶部绘制中文说明条（HR/技术均可读）。"""
    img = Image.open(src).convert("RGB")
    banner_h = 118
    out = Image.new("RGB", (img.width, img.height + banner_h), "#1e293b")
    out.paste(img, (0, banner_h))
    draw = ImageDraw.Draw(out)
    ok = status.upper() in ("PASS", "OK", "通过")
    color = "#22c55e" if ok else "#ef4444"
    draw.rectangle([0, 0, img.width, banner_h], fill="#0f172a")
    draw.rectangle([0, 0, 8, banner_h], fill=color)
    f_title = _font(20)
    f_body = _font(15)
    draw.text((18, 10), title, fill="white", font=f_title)
    draw.text((18, 38), f"【结果】{status}  ·  {hr_line}", fill="#e2e8f0", font=f_body)
    draw.text((18, 62), f"【技术】{tech_line}", fill="#94a3b8", font=f_body)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((18, 88), f"【时间】{ts}", fill="#64748b", font=f_body)
    if extra_lines:
        y = banner_h + img.height - 28 * len(extra_lines) - 8
        for line in extra_lines[-3:]:
            draw.rectangle([8, y, img.width - 8, y + 24], fill="#00000099")
            draw.text((14, y + 4), line[:90], fill="#fef08a", font=f_body)
            y += 26
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest, "PNG")
    if src != dest and src.exists():
        src.unlink(missing_ok=True)
    return dest


def _safe_filename(seq: int, slug: str, status: str) -> str:
    slug = re.sub(r"[^\w\u4e00-\u9fff\-]+", "_", slug).strip("_")[:56]
    st = "通过" if status.upper() in ("PASS", "OK", "通过") else "未通过"
    return f"{seq:02d}_{slug}_{st}.png"


class AgentBrowserCapture:
    """无头浏览器打开 /app/，只截页面视口（非全桌面）。"""

    def __init__(
        self,
        base_url: str,
        shot_dir: Path,
        *,
        viewport: Tuple[int, int] = (1400, 900),
        response_wait_ms: int = 45000,
    ) -> None:
        self.app_url = f"{base_url.rstrip('/')}/app/"
        self.shot_dir = shot_dir
        self.viewport = viewport
        self.response_wait_ms = response_wait_ms
        self._pw = None
        self._browser = None
        self.page = None
        self.records: List[Dict[str, Any]] = []

    def start(self) -> None:
        from playwright.sync_api import sync_playwright

        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=True)
        self.page = self._browser.new_page(
            viewport={"width": self.viewport[0], "height": self.viewport[1]}
        )
        self.page.goto(self.app_url, wait_until="domcontentloaded", timeout=30_000)

    def stop(self) -> None:
        if self._browser:
            self._browser.close()
        if self._pw:
            self._pw.stop()

    def select_developer_mode(self) -> None:
        assert self.page
        self.page.get_by_role("button", name="开发者模式").click()
        self.page.wait_for_timeout(600)

    def wait_service_online(self, timeout_ms: int = 30_000) -> bool:
        assert self.page
        try:
            self.page.get_by_text("服务在线", exact=False).wait_for(
                timeout=timeout_ms, state="visible"
            )
            return True
        except Exception:
            return False

    def send_chat_and_wait(self, text: str) -> None:
        assert self.page
        field = self.page.get_by_placeholder("输入任务，例如")
        field.click()
        field.fill(text)
        self.page.get_by_role("button", name="发送").click()
        self.page.wait_for_timeout(800)
        try:
            self.page.wait_for_function(
                """() => {
                  const t = document.body.innerText || '';
                  return !t.includes('正在思考') && !t.includes('正在执行任务');
                }""",
                timeout=self.response_wait_ms,
            )
        except Exception:
            self.page.wait_for_timeout(5000)

    def capture_step(
        self,
        seq: int,
        slug: str,
        *,
        title: str,
        hr_line: str,
        tech_line: str,
        status: str,
        extra_lines: Optional[List[str]] = None,
        chat_before: Optional[str] = None,
    ) -> Optional[str]:
        assert self.page
        if chat_before:
            self.send_chat_and_wait(chat_before)
            self.page.wait_for_timeout(500)

        raw = self.shot_dir / f"_raw_{seq}.png"
        self.page.screenshot(path=str(raw), full_page=False)

        fname = _safe_filename(seq, slug, status)
        dest = self.shot_dir / fname
        annotate_screenshot(
            raw,
            dest,
            title=title,
            hr_line=hr_line,
            tech_line=tech_line,
            status=status,
            extra_lines=extra_lines,
        )
        rec = {
            "seq": seq,
            "file": fname,
            "title": title,
            "hr_line": hr_line,
            "tech_line": tech_line,
            "status": status,
            "path": str(dest),
        }
        self.records.append(rec)
        return str(dest)

    def capture_overlay_only(
        self,
        seq: int,
        slug: str,
        *,
        title: str,
        hr_line: str,
        tech_line: str,
        status: str,
        extra_lines: Optional[List[str]] = None,
    ) -> Optional[str]:
        """不操作 UI，仅截当前控制台画面（用于 pytest 等）。"""
        return self.capture_step(
            seq,
            slug,
            title=title,
            hr_line=hr_line,
            tech_line=tech_line,
            status=status,
            extra_lines=extra_lines,
            chat_before=None,
        )
