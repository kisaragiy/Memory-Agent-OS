# 上传 GitHub 前核对（简历 vs 仓库）

## 结论：**可以上传**，简历描述与代码主干一致；上传前建议做一次整理提交。

---

## 简历逐项对照

| 简历表述 | 仓库实际情况 | 结论 |
|----------|--------------|------|
| Memory Agent OS · 2026.03–2026.05 | `README` / `SYSTEM_BLUEPRINT` 一致 | ✅ |
| Python / FastAPI / React | `agent_service/`、`web/frontend/` | ✅ |
| Ollama / Chroma | `core/memory/vector_store.py`，**可选**（无则 keyword 降级） | ✅ 写「可选集成」更准确 |
| 单内核 Orchestrator → ExecutionEngine → Tool | `KernelOrchestrator` → `ExecutionEngine` → `ToolRouter` | ✅（简历为简化表述） |
| AgentOSRuntime 唯一入口 | `core/runtime/agent_os_runtime.py` | ✅ |
| MemoryLayer + execute_memory_op | `memory_layer.py` + `memory_op_tool.py` | ✅ |
| 虚拟世界状态机 | `WorldRuntime` | ✅ |
| Guarded UI Automation | `guarded_ui_action_tool` + `ActionGuard` | ✅ |
| Phase5 observe-plan-act-reflect | `AutonomousOSLoop` | ✅ |
| NDJSON 流式 API | `POST /api/stream`、`/api/autonomous/stream` | ✅ |
| 桌面实况流 | `GET /api/desktop/stream` | ✅（WSL+Windows 环境） |
| 回归测试 | `tests/test_*.py` 共 8 个模块 | ✅ |

**无需改简历**；若面试官追问 Ollama，答：「语义检索可选，未安装时自动降级，trace 可观测。」

---

## 上传前注意（仓库卫生）

1. **勿提交**：`memory_db/`、`.env`（已在 `.gitignore`）
2. **建议忽略**：`docs/test_runs/`（已加入 `.gitignore`）
3. **历史提交里曾有误加文件**（如 `File: core/runtime/...`）：不影响简历真实性，公开前可用新提交删除或 `git filter-repo`（可选）
4. **简历 PDF**：已加入 `.gitignore`，**不会上传**；简历正文见 `docs/RESUME_CONTENT.md`（仅本地/自用）

---

## 上传步骤（在 WSL 项目目录执行）

### 1. 在 GitHub 网页新建仓库

- 名称建议：`Memory-Agent-OS` 或 `AgentOSSystem`
- **不要**勾选「Add README」（本地已有）
- 可见性：Public（作品集）或 Private

### 2. 本地提交并推送

```bash
cd ~/AgentOSSystem
git add -A
git status   # 确认无 memory_db、.env、test_runs
git commit -m "docs: HR test cases, portfolio README, gitignore for test runs"
git remote add origin https://github.com/kisaragiy/Memory-Agent-OS.git
git branch -M main
git push -u origin main
```

若已有 `origin` 但地址不对：

```bash
git remote set-url origin https://github.com/<用户名>/<仓库名>.git
git push -u origin main
```

### 3. README 置顶说明（面试官 30 秒能跑起来）

仓库首页已有：

```bash
./scripts/start_production.sh
# http://127.0.0.1:8787/app/
```

---

## 简历项目栏建议附链接

> Memory Agent OS（单内核 Agent Runtime）— GitHub: https://github.com/kisaragiy/Memory-Agent-OS

不录屏不影响可信度，**链接 + README 架构图** 即可。
