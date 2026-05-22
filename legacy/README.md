# Legacy / 非主路径代码

以下目录**不在** `AgentOSRuntime.entry()` 执行链上，保留仅供对照与历史参考。**禁止**在新功能中引用。

| 目录 | 说明 |
|------|------|
| `../agents/` | 旧版多 Agent router/planner/executor |
| `../api/` | 旧 HTTP 入口，调用 `agents.core` |
| `../core/kernel/*`（实验模块） | strategy_evolution、self_improving_loop 等，未接入生产内核 |
| `../core/memory/memory_store.py` 等 | 已由 `core/memory/memory_layer.py` 替代 |

**唯一生产路径**：`main.py` → `core/runtime/agent_os_runtime.py` → `agent_service/`
