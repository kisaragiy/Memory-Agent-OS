# Memory Agent OS — 使用说明

**版本**：2026.05 · **作者**：张伟强  
**适用**：作品集演示、功能测试、录屏展示

---

## 1. 系统简介

Memory Agent OS 是一套 **单内核 LLM Agent Runtime**（非普通 Chatbot）：

- 所有工具调用经唯一 `ExecutionEngine`
- 记忆显式写入可审计（治理化 mutation + trace）
- 支持虚拟世界状态机与 Phase5 自主闭环
- 开发者模式可查看完整执行 trace

---

## 2. 环境要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Linux / WSL2（推荐 Ubuntu 22.04） |
| Python | 3.10+ |
| Node.js | 构建前端时需 18+（首次启动脚本会自动 build） |
| 可选 | Ollama + `nomic-embed-text`（语义记忆检索） |
| 桌面实况 | WSL2 + Windows 主机（Phase5 桌面 MJPEG） |

---

## 3. 安装与启动

### 3.1 安装依赖

```bash
cd AgentOSSystem
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3.2 启动生产服务（API + Web UI）

```bash
./scripts/start_production.sh
```

浏览器打开：**http://127.0.0.1:8787/app/**

### 3.3 可选：桌面实况（WSL + Windows）

```bash
./scripts/run_desktop_wsl.sh
```

在开发者模式右侧查看 **桌面实况** 面板；流地址：`GET /api/desktop/stream`。

### 3.4 命令行

```bash
python3 main.py --mode developer --trace
python3 main.py --autonomous-session --autonomous-steps 4 "打开记事本"
```

---

## 4. Web 界面操作

### 4.1 模式切换

| 模式 | 说明 |
|------|------|
| user | 仅展示干净结果 |
| developer | 完整 trace、记忆治理、Phase5 控件 |
| debug | 更详细的执行链（若 UI 提供） |

**录屏建议**：全程使用 **开发者模式**。

### 4.2 典型对话示例

| 输入 | 预期行为 |
|------|----------|
| `1+2` | 走代码通道 `execute_code`，trace 可见 |
| `记住: 我叫张伟强` | 治理化记忆 `execute_memory_op` |
| 叙事类自然语言 | `narrative_respond` + World 状态更新 |
| 勾选 Phase5 + 目标描述 | 多步 `observe→plan→act→reflect` |

### 4.3 记忆治理（开发者）

通过 API 或 UI（若已接好）进行显式 mutation，路径必须为：

`MemoryControl` → `ExecutionEngine` → `execute_memory_op` → `MemoryLayer`

禁止直接编辑 `memory_db` 下 JSON 文件作为「功能演示」（会破坏治理叙事）。

---

## 5. 主要 HTTP API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/run` | 单轮内核执行 |
| POST | `/api/stream` | NDJSON 流式 |
| POST | `/api/autonomous/run` | Phase5 一次返回完整会话 |
| POST | `/api/autonomous/stream` | Phase5 逐步 NDJSON |
| GET | `/api/desktop/stream` | 桌面 MJPEG 实况 |
| GET | `/api/desktop/screenshot` | 单帧 PNG |
| POST | `/api/memory/mutate` | 治理化记忆写入 |

Swagger：**http://127.0.0.1:8787/docs**

---

## 6. 目录速查

| 路径 | 职责 |
|------|------|
| `main.py` | CLI 入口 |
| `core/runtime/agent_os_runtime.py` | 唯一系统入口 |
| `core/runtime/execution_engine.py` | 唯一执行引擎 |
| `core/memory/memory_layer.py` | 唯一记忆入口 |
| `core/control/model_policy.py` | 模型与能力边界策略 |
| `agent_service/` | FastAPI 生产服务 |
| `web/frontend/` | React 开发者控制台 |

架构约束文档：`SYSTEM_BLUEPRINT.md`、`ARCHITECTURE_CONSTRAINTS.md`。

---

## 7. 常见问题

**Q：前端空白或 404？**  
A：确认 `web/frontend/dist` 已构建，或重新执行 `start_production.sh`。

**Q：语义检索不工作？**  
A：检查 Ollama 是否运行；无嵌入服务时会 keyword 降级，trace `_meta` 可观测。

**Q：桌面实况黑屏？**  
A：在 WSL 环境运行 `scripts/verify_desktop_capture.py`，确认 Windows 侧捕获正常。

**Q：与 Chatbot 有何不同？**  
A：本系统强调 **可观测单核执行**、World 状态机、Guard、自主闭环与记忆治理，而非单纯对话封装。

---

## 8. 录屏前检查清单

- [ ] `pytest tests/ -q` 通过
- [ ] `./scripts/start_production.sh` 已启动，8787 可访问
- [ ] 浏览器开发者模式已打开
- [ ] 示例输入已准备好（见 `docs/VIDEO_SCRIPT.md`）
- [ ] （可选）桌面实况脚本已启动
