# 作品集展示指南

## 30 秒电梯演讲

「我实现了一套 **单内核 LLM Agent Runtime**：所有工具调用走唯一 `ExecutionEngine`，记忆写入可审计，并完成了 Phase5 的 observe-plan-act-reflect 自主闭环与开发者可观测 UI。」

## 推荐演示流程（5 分钟）

1. 启动：`./scripts/start_production.sh`
2. 打开 `http://127.0.0.1:8787/app/`，切换 **开发者模式**
3. 输入：`1+2` → 展示 **代码通道** 与 trace
4. 输入：`记住: 我叫张伟强` → 展示 **治理化记忆**
5. 勾选 **Phase5 自主循环**，输入简单目标 → 展示多步 NDJSON / trace
6. （可选 WSL）右侧 **桌面实况** 面板

## 面试官可能追问

| 问题 | 要点 |
|------|------|
| 为什么叫 OS？ | OS = **运行时内核**（调度、syscall、策略），不是 Windows 内核 |
| 如何保证单核？ | 禁止第二 ExecutionEngine；显式 mutation 仅 `execute_memory_op` |
| 与 Chatbot 区别？ | 有 World 状态机、Guard、自主闭环、可回放 trace |
| 技术难点？ | ModelPolicy 边界、Memory Governance、Guarded UI 与可观测降级 |

## 仓库链接占位

GitHub: `https://github.com/<your-username>/AgentOSSystem`（推送后替换）
