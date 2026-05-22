# SYSTEM BLUEPRINT — Memory Agent OS

> 提醒语：「遵守 SYSTEM_BLUEPRINT.md，不要偏离单核原则」

## 1. 项目本质（不可修改）

本项目是：**LLM 驱动的操作系统级 Agent Runtime + 虚拟叙事世界引擎**

不是：chatbot / workflow tool / LLM API wrapper / 单一 AI 应用。

是：AI OS · Agent Runtime Kernel · Virtual World Simulation · Multi-Agent Cognitive System。

## 2. 系统目标（长期不变）

- **智能**：多步规划、编程、长文本、Prompt 工程、漫剧、多模态
- **虚拟世界**：角色一致性、关系图谱、情绪传播、剧情状态机、叙事 Runtime
- **现实交互（未来）**：屏幕理解、键鼠自动化、OS 级任务
- **内容生成**：漫剧、视频 pipeline、TTS、音乐、剪辑

## 3. 架构原则

### 3.1 Single Kernel Principle

唯一执行路径，禁止多 router / 多 execution engine / 多 memory 主入口。

### 3.2 Deterministic Execution

Tool 可追踪、execution 有 trace、禁止 silent failure。

### 3.3 Cognitive Separation

Kernel · Brain · Memory · World · Renderer — 禁止混合实现。

### 3.4 Closed Loop

plan → act → observe → reflect → retry

## 4. 工程六层（现实版）

```
Presentation (UI)
    ↓
Control (模式 / debug / trace)      ← BIOS
    ↓
Orchestration (planner / agent)
    ↓
Execution (tool / sandbox)          ← 当前收敛重点
    ↓
State (memory)
    ↓
World (小说 / 漫剧 / 模拟 — 插件化)
```

| 模式 | 输出 |
|------|------|
| user | 干净结果 |
| developer | 完整 trace |
| debug | 全部执行链 |

## 5. 唯一执行路径（必须遵守）

```
main.py
  → AgentOSRuntime.entry()
      → InputNormalizer → MemoryLayer.build_context (Claude-grade)
      → WorldRuntime.step (纯状态，持久化经 MemoryLayer)
      → [4A] PerceptionGate → ScreenObserver (只读)
      → [4B] ActionPlanBuilder → ActionPlan
      → [4C] ActionGuard → (确认后) ExecutionEngine → guarded_ui_action → Sandbox
      → KernelOrchestrator.build_plan (Brain)
      → SchemaGate → ExecutionEngine (唯一)
          → ToolRouter → Tool (execute_code | narrative_respond)
              → narrative_respond 内 NarrativeWriter.render（Renderer，只读 state）
      → WorldRuntime.apply_turn (纯状态) → MemoryLayer.record_episode → ReflectionLoop
```

## 6. 禁止原则

- 多 execution engine / 多 tool router
- memory 分裂实现
- silent fallback
- execution 无 trace
- 未注册工具隐式执行

## 7. 演化阶段

| Phase | 状态 |
|-------|------|
| 1 Kernel stabilization | 已完成（遗留重复 router/engine 已清理） |
| 2 Memory unified + planner/reflection | 已完成（见 §11 Claude 记忆层清单） |
| 3 World Engine | 已完成（纯状态 World + Renderer） |
| 4A Screen observation | 已完成（只读） |
| 4B Action planning | 已完成 |
| 4C Guarded execution | 已完成 |
| 4D Autonomous control | 已完成（vision + live driver + auto-confirm） |
| 5 Autonomous agent OS | 已完成（闭环 + 桌面实况流） |

## 8. 当前阶段

**Phase 5 — Autonomous Agent OS** — 多步闭环 `observe → plan → act → reflect`（`AutonomousOSLoop` → 重复 `entry()`）；桌面 **实况流** `/api/desktop/stream`；自主会话 API `/api/autonomous/run|stream`。执行权仍在唯一 `ExecutionEngine`。

## 15. Phase 5 — Autonomous Agent OS

**Brain**：`core/orchestration/autonomous_loop.py` — `AutonomousOSLoop`（禁止第二 engine）

**Runtime**：`AgentOSRuntime.run_autonomous_session()` / `iter_autonomous_session()` — 每步仅调用 `entry()`

**实况（直播式预览）**：

| 端点 | 用途 |
|------|------|
| `GET /api/desktop/stream` | MJPEG multipart，UI `<img src=…>` 约 1.2s 刷新 |
| `GET /api/desktop/screenshot` | 单帧 PNG |
| `POST /api/autonomous/run` | 一次返回完整自主会话 |
| `POST /api/autonomous/stream` | NDJSON 逐步推送 |
| `POST /api/run` + `autonomous_session: true` | 与聊天流集成 |

**前端**：开发者模式 — `DesktopLivePanel` + ModeBar「Phase5 自主循环」

**启动**（WSL）：

```bash
./scripts/run_desktop_wsl.sh
# 浏览器 developer 模式 → 右侧「桌面实况」+ 勾选 Phase5 自主循环
```

## 9. 核心映射

- Memory = 世界状态
- Agent = 行为系统
- Kernel = 执行系统
- World = 模拟系统（插件）
- Renderer = 表现系统

## 10. 最高原则

**一切必须收敛到单一可观测执行内核。**

## 11. Claude 级记忆层（唯一入口 `core/memory/memory_layer.py`）

| 能力 | 状态 | 实现 |
|------|------|------|
| 短期对话（conversation.jsonl） | ✅ | `PersistentStore` |
| 长期事实 / 偏好（records.json） | ✅ | `remember` + `extract_memories` |
| 语义检索（Chroma + Ollama embed） | ✅ | `VectorStore`，失败则 keyword |
| 情节记忆（episodes.json 持久化） | ✅ | `record_episode` → `episodes.json` |
| 项目 / 世界观槽位 | ✅ | `project.json` + `narrative_schema.json` |
| 世界状态快照 | ✅ | `world.json` via MemoryLayer |
| 对话压缩摘要 | ✅ | `summarizer` + `consolidator` → schema.long_term |
| 访问计数 / 去重 | ✅ | `memory_policy` |
| 反思写回（procedural） | ✅ | `apply_reflection`（可观测，非 silent） |
| 程序性提示 | ✅ | `_procedural_hints` |
| 控制层意图 → 记忆通道 | ✅ | `IntentRouter` MEMORY → `remember` |

**未纳入主路径（禁止新入口）**：`core/memory/memory_store.py`、`memory_brain.py` 等为遗留，仅 `SchemaMigrator` 读取旧 `memory_schema.json`。

**依赖**：语义检索需本机 Ollama + `nomic-embed-text`；无 Chroma/Ollama 时自动 keyword 降级（`_meta` 可观测）。

## 12. Memory Governance（受控编辑 — 非数据库 CRUD）

**原则（不可违反）**：

- Memory = **governed state machine**（不是 JSON/Chroma 数据库）
- 所有 **显式 mutation** 必须 **trace**（`mutation_trace.jsonl`）
- 所有 **显式写** 必须经过 **ExecutionEngine → execute_memory_op → MemoryLayer.apply_mutation**
- 禁止 UI/API/CLI **直写** `memory_db`、Chroma、sqlite
- 禁止 bypass MemoryLayer

**唯一 mutation 路径**：

```
UI / API / CLI
  → MemoryControl.authorize (Control)
    → MemoryControl.build_kernel_plan (Orchestration)
      → ExecutionEngine → execute_memory_op (Kernel)
        → MemoryLayer.apply_mutation (State)
```

**Intent 格式（禁止 `{ "update": xxx }` CRUD）**：

```json
{
  "op": "update_memory",
  "target": "semantic",
  "action": "merge | delete | override | inject | snapshot | rollback",
  "fact": "...",
  "record_id": "...",
  "snapshot_id": "..."
}
```

| 类型 | dev 可改 | 规则 |
|------|----------|------|
| episodic | ❌ 直改 | 仅 snapshot / rollback |
| semantic | ✅ | merge / delete / override / inject |
| procedural | ⚠️ debug only | 必须 trace |
| world_state | ❌ 直改 | 仅 World Engine → save_world_state |

**闭环自动抽取**（`record_episode` → `ingest_user_message`）属于内核闭环内部写入，与用户显式编辑区分；显式编辑一律走 `execute_memory_op`。

## 13. Model Policy（唯一策略层 `core/control/model_policy.py`）

**核心原则**：

- **Model ≠ intelligence** — 模型是执行单元，不是决策系统
- **Policy = intelligence boundary** — 能力调制、安全边界、输出约束集中在 `ModelPolicy`
- **Orchestrator = decision system** — Intent 分类 + 路由（code / llm / memory / guard）
- **ExecutionEngine = deterministic runtime** — 只执行 syscall，不做策略判断

**禁止**：

- ❌ execution layer 拼 prompt / 定 mode
- ❌ memory layer 控制 LLM 输出风格
- ❌ `core/llm/client.py` 做策略或 mode 判断
- ❌ 多处 system prompt 拼接

**Intent 路由表（Orchestrator）**：

| 输入类型 | 路由 |
|----------|------|
| `1+2` / `print(...)` / `x=5` 等安全 Python | `execute_code` |
| 自然语言（聊天 / 叙事） | `llm` → `narrative_respond` |
| `remember:` / `记住:` | `memory` → `execute_memory_op` |
| UI action plan | `guard` |

**ModelMode**（`user` / `developer` / `creative` / `strict`）定义：`max_tokens`、`temperature`、`allow_reasoning`、`allow_trace`、`allow_narrative`、`output_style`。`ModelPolicy` 生成 `LLMInvocationSpec`；`invoke_llm` / `call_vision` 仅传输。

14.Single Policy Enforcement Rule（）

任何 LLM 调用必须通过 ModelPolicy

禁止：

direct call_llm()
direct prompt assembly
internal summarizer LLM calls bypassing policy
2. No Secondary Brain Rule（非常关键）

系统中禁止存在第二类“决策模块”：

禁止：

judge acting as planner
evaluator generating prompts
executor making routing decisions

只能有：

Orchestrator = 唯一 decision point

3. Execution Engine must be stateless

必须明确：

ExecutionEngine 不得做任何“判断”
不得 fallback routing
不得 retry logic
不得 tool selection

只做：

syscall → tool → result

4. Memory Write Authority Rule

必须明确：

只有 MemoryLayer 可以写 state

禁止：

world 写 memory
tool 写 memory
planner 写 memory
5. Intent Trace Requirement（你现在很关键的一点）

每一次执行必须记录：

intent_trace = {
  "input": "...",
  "intent": "llm / code / memory",
  "mode": "user/dev",
  "route": "...",
  "policy": "...",
}

禁止：
在 orchestrator 做 output filtering
在 execution engine 做字段裁剪
在 llm client 做信息隐藏
在 memory 层做展示控制。
