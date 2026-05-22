# Architecture Hard Constraints

> 与 `SYSTEM_BLUEPRINT.md` 同等效力。违反即视为分裂内核。

## 1. 唯一执行权

**仅** `core/runtime/execution_engine.py` 可 dispatch tool / sandbox / subprocess。

禁止 WorldRuntime、NarrativeWriter、EmotionEngine、Reflection、Planner、CharacterGraph 直接执行或路由。

## 2. World 纯状态化

`WorldRuntime` 只允许：update state · generate context · transitions · constraints。

禁止：写文件 · 调 tool · 网络 · shell。持久化 **仅** 经 `memory_layer.py`。

## 3. Renderer 分层

`core/renderer/narrative_writer.py`：`render(state → output)` only。

禁止：参与 planner · 改 world · 写 memory。

## 4. 唯一 Memory 入口

**仅** `core/memory/memory_layer.py` 可读写 Chroma / json / memory_db / embedding。

显式 mutation **仅** `MemoryLayer.apply_mutation()`，且必须由 `execute_memory_op` 经 `ExecutionEngine` 调用。治理层：`core/control/memory_control.py`。

## 5. Fallback 可观测

必须：`_meta.source` · `reflection.sources` · trace · 禁止 `except: pass` 隐式降级。

## 6. 状态契约

使用 `core/contracts/`：`WorldState` `CharacterState` `EmotionState` `NarrativeState` `MemoryRecordContract` `ReflectionRecord` `ObservationState`。

## 7. 禁止新 planner/router/executor 命名

除非替换 canonical path，不得新增同名分裂模块。

## 8. Phase 4 顺序

- **4A** Observation：屏幕/UI 理解，只读
- **4B** Action planning：`ActionPlanBuilder` 产出 intents
- **4C** Guarded execution（当前）：`ActionGuard` + `guarded_ui_action` 仅经 `ExecutionEngine`；默认 dry-run
- **4D** Autonomous control（当前）：`AutonomyPolicy` + `VisionObserver` + `OsAutomationDriver`（仅 Sandbox 调用）

禁止跳过 guard 直接 pyautogui / shell 自动化。
