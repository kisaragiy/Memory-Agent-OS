# Memory Agent OS

> LLM 驱动的单内核 Agent Runtime + 虚拟叙事世界引擎 · 作品集主仓库

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](requirements.txt)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](agent_service/app.py)

## 项目定位

**不是** Chatbot / Workflow 封装，而是可观测的 **Agent OS 内核**：

- 唯一执行路径：`main.py` → `AgentOSRuntime.entry()` → `ExecutionEngine`
- 治理化记忆：显式写入经 `execute_memory_op`，全链路 trace
- 世界状态机：角色 / 情绪 / 叙事 Runtime（纯状态，经 MemoryLayer 持久化）
- Phase 5 自主闭环：`observe → plan → act → reflect` + 开发者桌面实况流

架构约束见 [`SYSTEM_BLUEPRINT.md`](SYSTEM_BLUEPRINT.md)、[`ARCHITECTURE_CONSTRAINTS.md`](ARCHITECTURE_CONSTRAINTS.md)。

## 架构一览

```
Presentation (React / FastAPI)
    ↓
Control (user / developer / debug · ModelPolicy)
    ↓
Orchestration (KernelOrchestrator · AutonomousOSLoop)
    ↓
Execution (ExecutionEngine → ToolRouter → tools)
    ↓
State (MemoryLayer · Chroma/Ollama 可选)
    ↓
World (WorldRuntime · NarrativeWriter)
```

## 快速开始

### 1. 环境

```bash
cd AgentOSSystem
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

可选（语义检索）：本机 [Ollama](https://ollama.com/) + `ollama pull nomic-embed-text`。

### 2. 启动 API + Web UI

```bash
./scripts/start_production.sh
# 浏览器打开 http://127.0.0.1:8787/app/
```

开发者模式可查看执行 trace、记忆治理与 Phase5 自主循环。

### 3. WSL + Windows 桌面（可选）

```bash
./scripts/run_desktop_wsl.sh
# 实况流: http://127.0.0.1:8787/api/desktop/stream
```

需 WSL2 + Windows 主机；详见 `scripts/verify_desktop_capture.py`。

### 4. CLI

```bash
python3 main.py --mode developer --trace
python3 main.py --autonomous-session --autonomous-steps 4 "打开记事本"
```

## 测试

```bash
python3 -m pytest tests/ -q
```

覆盖：对齐策略、记忆治理、自主循环、Phase4 Guard、ModelPolicy 等。

## 演示文档（录屏 / 答辩）

```bash
./scripts/build_portfolio_docs.sh
# 或: pip install -r requirements-docs.txt && python3 scripts/generate_portfolio_docs.py
```

生成物：

| 文件 | 说明 |
|------|------|
| `docs/MemoryAgentOS-系统架构说明.docx` | 架构说明 + 分层/执行路径图 |
| `docs/MemoryAgentOS-使用说明.docx` | 安装、界面、API |
| `docs/MemoryAgentOS-测试与演示指南.docx` | 冒烟清单 + 5 分钟演示流程 |
| `docs/diagrams/*.png` | 架构位图 |
| `docs/VIDEO_SCRIPT.md` | 录屏分镜与口播稿 |
| `docs/HR_TEST_CASES.md` | **HR 可读**手工测试用例（录屏打勾表） |
| `docs/ARCHITECTURE_DIAGRAM.md` | Mermaid 图源（GitHub/VS Code 预览） |

### 后台一键测试 + Agent 浏览器截图（HR 可读）

Windows 双击：`desktop-os-tests/后台自动测试截图.cmd`（自动起服务、仅截 `/app/`、打开 `report_hr.html`）

```bash
pip install -r requirements-test-capture.txt && python3 -m playwright install chromium
python3 scripts/background_test_capture.py --hr --browser-only --start-server --open-report
```

输出：`docs/test_runs/<时间戳>/report_hr.html`，截图如 `02_基础计算_1加2等于3_通过.png`（图顶有中文备注条）

## 主要 API

| 端点 | 说明 |
|------|------|
| `POST /api/run` | 单轮内核执行 |
| `POST /api/stream` | NDJSON 流式 |
| `POST /api/autonomous/run` | Phase5 多步自主会话 |
| `GET /api/desktop/stream` | 桌面 MJPEG 实况（开发者） |
| `POST /api/memory/mutate` | 治理化记忆写入 |

完整列表：`http://127.0.0.1:8787/docs`

## 目录说明

| 路径 | 说明 |
|------|------|
| `core/runtime/agent_os_runtime.py` | **唯一系统入口** |
| `core/runtime/execution_engine.py` | 唯一执行引擎 |
| `core/memory/memory_layer.py` | 唯一记忆入口 |
| `agent_service/` | 生产 FastAPI |
| `web/frontend/` | React 开发者控制台 |
| `legacy/` | 非主路径历史代码说明 |
| `tests/` | 内核回归测试 |

## Roadmap（未纳入当前成品）

- 漫剧 / 视频 / TTS 内容管线（Blueprint §2 远期）
- 跨平台桌面自动化（当前以 WSL+Windows 为主）

## 仓库

https://github.com/kisaragiy/Memory-Agent-OS

## 作者

张伟强 · 2026.03 — 2026.05

## License

MIT（作品集展示用途）
