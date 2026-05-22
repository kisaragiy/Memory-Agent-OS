# -*- coding: utf-8 -*-
"""Generate resume PDF (WSL/Linux or Windows). Outputs to docs/ and optionally C:\\面试\\"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DOCS.mkdir(parents=True, exist_ok=True)

OUT_WSL = DOCS / "张伟强-后端开发.pdf"
WIN_DIR = Path(r"C:\面试") if sys.platform == "win32" else None
OUT_WIN = WIN_DIR / "张伟强-后端开发.pdf" if WIN_DIR else None
BACKUP_WIN = WIN_DIR / "张伟强-后端开发-原版备份.pdf" if WIN_DIR else None
VERIFY = DOCS / "resume_verify.txt"

FONT_CANDIDATES = [
    Path(r"C:\Windows\Fonts\msyh.ttc"),
    Path(r"C:\Windows\Fonts\simhei.ttf"),
    Path("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
]

from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_LEFT  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import getSampleStyleSheet  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402


def register_cn_font() -> str:
    for path in FONT_CANDIDATES:
        if path.is_file():
            name = "CNFont"
            if path.suffix.lower() == ".ttc":
                pdfmetrics.registerFont(TTFont(name, str(path), subfontIndex=0))
            else:
                pdfmetrics.registerFont(TTFont(name, str(path)))
            return name
    raise FileNotFoundError("No CJK font; install fonts-wqy-zenhei or use Windows")


def build_story(font_name: str):
    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title", fontName=font_name, fontSize=20, leading=24, spaceAfter=4)
    subtitle = ParagraphStyle(
        "Subtitle", fontName=font_name, fontSize=9, leading=12, textColor=colors.HexColor("#333333"), spaceAfter=10
    )
    h2 = ParagraphStyle(
        "H2", fontName=font_name, fontSize=11, leading=14, spaceBefore=8, spaceAfter=4, textColor=colors.HexColor("#1a1a1a")
    )
    h3 = ParagraphStyle("H3", fontName=font_name, fontSize=10, leading=13, spaceBefore=4, spaceAfter=2)
    body = ParagraphStyle("Body", fontName=font_name, fontSize=9, leading=13, spaceAfter=2)
    bullet = ParagraphStyle("Bullet", parent=body, leftIndent=12, spaceBefore=1)

    s = []
    s.append(Paragraph("张伟强", title))
    s.append(
        Paragraph(
            "25届应届毕业生 &nbsp;|&nbsp; 22岁 &nbsp;|&nbsp; 广东省东莞市 &nbsp;|&nbsp; "
            "全日制本科 &nbsp;|&nbsp; 15377798768 &nbsp;|&nbsp; taqibala@outlook.com",
            subtitle,
        )
    )
    s.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    s.append(Paragraph("求职意向", h2))
    s.append(Paragraph("全职 &nbsp;&nbsp; Java / Python 后端开发工程师 &nbsp;&nbsp; 广州/深圳 &nbsp;&nbsp; 随时到岗", body))
    s.append(Paragraph("实习经验", h2))
    s.append(Paragraph("<b>2024.11 - 2025.01</b> &nbsp;&nbsp; 广州粤嵌通信科技有限公司 &nbsp;&nbsp; Java开发实习生", h3))
    for line in [
        "参与用户管理系统后端开发，使用 Spring Boot + MyBatis 实现用户信息的增删改查接口，编写并调试多表关联 SQL，接口通过 Postman 验证无误。",
        "独立完成登录模块的 Session 管理逻辑，处理登录态校验与接口权限拦截。",
        "配合前端完成 5 个业务接口的联调，排查并修复 2 处参数绑定异常。",
        "学习 Redis 缓存机制，在用户信息查询场景下完成缓存读取逻辑验证。",
    ]:
        s.append(Paragraph(f"· {line}", bullet))
    s.append(Paragraph("项目经历", h2))
    s.append(Paragraph("<b>2026.03 - 2026.05</b> &nbsp;&nbsp; Memory Agent OS（LLM 单内核 Agent Runtime）", h3))
    s.append(
        Paragraph(
            "<b>技术栈：</b>Python / FastAPI / React / Ollama / Chroma / 治理化记忆 / Guarded UI Automation",
            body,
        )
    )
    s.append(
        Paragraph(
            "<b>项目描述：</b>基于 Python 的单内核 LLM Agent Runtime，统一执行路径"
            "（Orchestrator → ExecutionEngine → Tool），集成治理化记忆层、虚拟世界状态机"
            "与受 Guard 约束的桌面自动化；提供 FastAPI 生产接口与 React 开发者控制台，"
            "支持 Phase5 observe-plan-act-reflect 自主闭环及执行链 trace 回放。",
            body,
        )
    )
    s.append(Paragraph("<b>个人职责：</b>", body))
    for line in [
        "设计并实现唯一系统入口 AgentOSRuntime，落地 Single Kernel 架构与 ModelPolicy 能力边界。",
        "实现 MemoryLayer 治理化记忆，显式写入经 execute_memory_op，配套 mutation trace 可审计。",
        "开发 FastAPI 服务与 NDJSON 流式 API，对接 React 开发者模式与桌面实况流（Phase5）。",
        "完成感知-规划-Guard 执行-反思闭环及 UI 自动化沙箱，保证执行可追踪、无 silent fallback。",
        "编写对齐策略、记忆治理、自主循环等回归测试，支撑作品集可复现演示。",
    ]:
        s.append(Paragraph(f"· {line}", bullet))
    s.append(Paragraph("<b>2025.02 - 2025.09</b> &nbsp;&nbsp; 电影推荐系统", h3))
    s.append(
        Paragraph(
            "<b>技术栈：</b>Spring Boot / MyBatis / MySQL / Redis / Vue.js / Spring Cloud Eureka",
            body,
        )
    )
    s.append(
        Paragraph(
            "<b>项目描述：</b>基于 Spring Boot + Vue.js 的前后端分离电影推荐平台，包含用户认证、"
            "电影信息管理、个性化推荐和后台管理四个核心模块。毕业后对项目进行架构重构，"
            "引入 Spring Cloud Eureka 完成服务注册配置，对各功能模块进行拆分设计。",
            body,
        )
    )
    s.append(Paragraph("<b>个人职责：</b>", body))
    for line in [
        "设计用户认证模块，基于 Session + 拦截器实现登录校验与接口权限控制，完成注册、登录、找回密码全流程。",
        "实现电影信息管理功能，支持增删改查、分类筛选与批量操作，集成 PageHelper 完成分页查询。",
        "基于用户观影记录构建协同过滤推荐模块，结合电影标签实现内容推荐逻辑。",
        "引入 Spring Cloud Eureka 完成服务注册与发现配置，对项目进行模块化拆分改造。",
        "使用 Redis 对高频查询的电影列表数据进行缓存处理，减少数据库重复查询。",
        "完成项目 Docker 化部署，在 Linux 环境下通过命令行进行服务启动与日志排查。",
    ]:
        s.append(Paragraph(f"· {line}", bullet))
    s.append(Paragraph("技能特长", h2))
    for line in [
        "熟练使用 Spring Boot + MyBatis + MySQL 进行后端服务开发，能够独立完成 RESTful 接口设计、业务逻辑实现与接口联调。",
        "熟练使用 Python + FastAPI 构建 Agent Runtime 与流式 API，理解单内核编排、工具 syscall 与执行链 trace 设计。",
        "了解 LLM 应用架构：治理化记忆、意图路由、ModelPolicy 输出约束；具备 Ollama/Chroma 语义检索集成经验。",
        "有 Spring Cloud Eureka 服务注册与发现配置经验，了解微服务模块拆分思路，能参与分布式系统的开发与维护。",
        "熟悉 Redis 缓存在热点数据场景下的应用，有基于用户行为数据构建协同过滤推荐模块的实践经验。",
        "能熟练使用 Postman 进行接口测试，掌握 Linux 基础命令，可在 Ubuntu/WSL 环境下完成服务部署与日志排查。",
        "注重代码可读性与接口规范，具备独立完成需求分析、模块开发到功能验证的全流程能力。",
    ]:
        s.append(Paragraph(line, body))
    s.append(Spacer(1, 6 * mm))
    s.append(Paragraph("教育背景", h2))
    s.append(
        Paragraph(
            "<b>2021.08 - 2025.06</b> &nbsp;&nbsp; 广州工商学院 &nbsp;&nbsp; 全日制本科 &nbsp;&nbsp; 软件工程专业",
            h3,
        )
    )
    s.append(
        Paragraph(
            "主修课程：Java程序设计、数据结构与算法、数据库原理、Linux操作系统、计算机网络、Python程序设计",
            body,
        )
    )
    return s


def write_pdf(path: Path, font_name: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
    )
    doc.build(build_story(font_name))
    return path.stat().st_size


def main() -> int:
    try:
        import reportlab  # noqa: F401
    except ImportError:
        os.system(f"{sys.executable} -m pip install reportlab -q")
    font = register_cn_font()
    size_wsl = write_pdf(OUT_WSL, font)
    lines = [f"OK wsl_pdf={OUT_WSL} bytes={size_wsl}"]
    if OUT_WIN and WIN_DIR and WIN_DIR.is_dir():
        src = OUT_WSL
        if OUT_WIN.exists() and BACKUP_WIN and not BACKUP_WIN.exists():
            shutil.copy2(OUT_WIN, BACKUP_WIN)
            lines.append(f"backup={BACKUP_WIN}")
        shutil.copy2(src, OUT_WIN)
        lines.append(f"copied_to={OUT_WIN} bytes={OUT_WIN.stat().st_size}")
    try:
        from pypdf import PdfReader

        t = "".join((p.extract_text() or "") for p in PdfReader(str(OUT_WSL)).pages)
        lines.append(f"has_agent_os={'Memory Agent OS' in t}")
        lines.append(f"has_2026={'2026.03' in t}")
    except Exception as e:
        lines.append(f"pypdf_note={e}")
    VERIFY.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
