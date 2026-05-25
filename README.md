# Memory Agent OS

> 基于 Python、FastAPI 与 React 的单内核 LLM Agent Runtime，集成治理化记忆、虚拟世界状态机与 Phase5 自主闭环（observe → plan → act → reflect），提供可观测执行 trace 与开发者控制台。

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](requirements.txt)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](agent_service/app.py)

## 项目简介

可观测的 **Agent OS 内核**（非 Chatbot 封装）：

- 唯一执行路径：`main.py` → `AgentOSRuntime.entry()` → `ExecutionEngine`
- 治理化记忆：显式写入经 `execute_memory_op`，全链路 trace
- 世界状态机：角色 / 情绪 / 叙事 Runtime（纯状态，经 MemoryLayer 持久化）
- Phase 5：多步自主闭环 + 可选桌面实况流（WSL + Windows）

架构约束见 [`SYSTEM_BLUEPRINT.md`](SYSTEM_BLUEPRINT.md)、[`ARCHITECTURE_CONSTRAINTS.md`](ARCHITECTURE_CONSTRAINTS.md)。

## 架构

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

```bash
git clone https://github.com/kisaragiy/Memory-Agent-OS.git
cd Memory-Agent-OS
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
./scripts/start_production.sh
# 浏览器 http://127.0.0.1:8787/app/  （开发者模式可查看 trace）
```

可选语义检索：本机 [Ollama](https://ollama.com/) + `ollama pull nomic-embed-text`。

桌面实况（可选）：`./scripts/run_desktop_wsl.sh` → `/api/desktop/stream`

## 测试

```bash
python3 -m pytest tests/ -q
```

## 文档

| 文档 | 说明 |
|------|------|
| [ARCHITECTURE_DIAGRAM.md](docs/ARCHITECTURE_DIAGRAM.md) | 架构图（Mermaid） |
| [USER_MANUAL.md](docs/USER_MANUAL.md) | 安装与使用 |
| [TEST_GUIDE.md](docs/TEST_GUIDE.md) | 测试指南 |

## 主要 API

| 端点 | 说明 |
|------|------|
| `POST /api/run` | 单轮执行 |
| `POST /api/stream` | NDJSON 流式 |
| `POST /api/autonomous/run` | Phase5 自主会话 |
| `GET /api/desktop/stream` | 桌面 MJPEG（开发者） |
| `POST /api/memory/mutate` | 治理化记忆写入 |

完整列表：http://127.0.0.1:8787/docs

## 目录

| 路径 | 说明 |
|------|------|
| `core/runtime/` | 系统入口与执行引擎 |
| `core/memory/` | 记忆层 |
| `agent_service/` | FastAPI 服务 |
| `web/frontend/` | React 控制台 |
| `tests/` | 回归测试 |
| `legacy/` | 历史代码说明（非生产路径） |

## License

MIT
