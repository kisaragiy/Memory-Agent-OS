# Memory Agent OS — 录屏脚本（约 5–8 分钟）

> 按 `PORTFOLIO.md` 推荐流程扩展，适合作品集 / 答辩演示。

---

## 0. 录制准备（片头前完成，不录入正片）

1. 终端：`cd AgentOSSystem && source .venv/bin/activate`
2. 测试：`python3 -m pytest tests/ -q`（可选口播「回归已通过」）
3. 启动：`./scripts/start_production.sh`
4. 浏览器预开：`http://127.0.0.1:8787/app/`，**开发者模式**
5. 录屏分辨率建议 1920×1080，放大浏览器 110–125%
6. （可选 WSL 桌面）另终端：`./scripts/run_desktop_wsl.sh`

---

## 1. 片头（0:00 – 0:30）

**画面**：README 或架构图 docx / `docs/diagrams/layers.png`

**口播示例**：

> 这是 Memory Agent OS：一套单内核 LLM Agent Runtime。不是 Chatbot 封装，而是可观测的执行内核——所有工具走唯一 ExecutionEngine，记忆写入可审计，并完成 Phase5 的 observe-plan-act-reflect 自主闭环。

---

## 2. 启动与界面（0:30 – 1:00）

**画面**：终端 `start_production.sh` 日志 → 浏览器 App 首页

**操作**：

- 指出地址栏 `8787/app`
- 点击切换到 **开发者模式**

**口播**：

> 生产栈是 FastAPI 加 React 开发者控制台。开发者模式会暴露完整 trace，方便证明「单核可观测」。

---

## 3. 代码通道演示（1:00 – 2:00）

**输入**：`1+2`

**画面**：展开 trace，标出 `execute_code` / intent / policy

**口播**：

> 像 `1+2` 这类安全 Python 表达式，Orchestrator 会路由到代码工具，而不是随便调 LLM。策略边界在 ModelPolicy，执行在 ExecutionEngine。

**可选第二输入**：`print("hello agent os")`

---

## 4. 治理化记忆（2:00 – 3:00）

**输入**：`记住: 我叫张伟强`

**画面**：trace 中 `memory` / `execute_memory_op`；若有记忆面板则点开

**口播**：

> 显式记忆不走 UI 直写 JSON，而是 MemoryControl 授权后，经 ExecutionEngine 的 execute_memory_op 写入 MemoryLayer，并记录 mutation trace。

---

## 5. 叙事 / 世界状态（3:00 – 4:00，可选）

**输入**：一句短叙事，如：`用小说口吻介绍你自己，两句话。`

**画面**：`narrative_respond` 与 World 相关 trace

**口播**：

> WorldRuntime 只维护纯状态，表现由 NarrativeWriter 渲染，不越权执行工具。

---

## 6. Phase5 自主循环（4:00 – 6:00）

**操作**：

1. 勾选 **Phase5 自主循环**
2. 输入简单目标，如：`列出当前目录下的前 3 个文件名` 或 `打开记事本`（视环境能力）
3. 展示 NDJSON 流或多步 trace

**口播**：

> AutonomousOSLoop 每一步只调用 entry()，没有第二个执行引擎。闭环是 observe、plan、act、reflect，适合作为 Agent OS 而非单次问答的证明。

---

## 7. 桌面实况（6:00 – 7:00，WSL 环境可选）

**画面**：右侧 **桌面实况** 面板 / `img` 刷新 MJPEG

**口播**：

> Phase5 在 WSL 下可接 Windows 桌面捕获，实况流在 `/api/desktop/stream`，用于观察 guarded UI 执行，而不是黑盒自动化。

---

## 8. 片尾（7:00 – 8:00）

**画面**：Swagger `/docs` 或架构 docx 目录页

**口播**：

> 仓库含完整 pytest、SYSTEM_BLUEPRINT 约束文档，以及自动生成的架构说明与测试指南 docx。谢谢观看。

---

## 9. 分镜对照表

| 序号 | 时长 | 画面 | 关键词 |
|------|------|------|--------|
| 1 | 30s | 架构图 | 单内核、Agent OS |
| 2 | 30s | 启动 UI | FastAPI、开发者模式 |
| 3 | 60s | 1+2 | execute_code、trace |
| 4 | 60s | 记住: | execute_memory_op |
| 5 | 60s | 叙事 | World、Renderer |
| 6 | 120s | Phase5 | 自主闭环 |
| 7 | 60s | 桌面实况 | MJPEG、WSL |
| 8 | 60s | API/docs | 可交付文档 |

---

## 10. 备用镜头（时间不够可删）

- CLI：`python3 main.py --mode developer --trace`
- `POST /api/autonomous/stream` 用 curl 或 Postman
- `pytest tests/ -q` 终端绿条
