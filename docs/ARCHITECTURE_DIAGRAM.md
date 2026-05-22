# Memory Agent OS — 架构图（Mermaid）

> 可在 VS Code / GitHub 预览；运行 `python3 scripts/generate_portfolio_docs.py` 生成 PNG 并写入 docx。

## 1. 六层工程架构

```mermaid
flowchart TB
    subgraph P["Presentation 表现层"]
        UI["React Web UI / FastAPI"]
    end
    subgraph C["Control 控制层"]
        MP["ModelPolicy · MemoryControl · BIOS 模式"]
    end
    subgraph O["Orchestration 编排层"]
        KO["KernelOrchestrator"]
        AL["AutonomousOSLoop Phase5"]
    end
    subgraph E["Execution 执行层"]
        EE["ExecutionEngine 唯一"]
        TR["ToolRouter"]
        T["Tools: execute_code · narrative_respond · execute_memory_op · guarded_ui_action"]
    end
    subgraph S["State 状态层"]
        ML["MemoryLayer 唯一记忆入口"]
        VS["VectorStore / Chroma 可选"]
    end
    subgraph W["World 世界层"]
        WR["WorldRuntime 纯状态"]
        NW["NarrativeWriter Renderer"]
    end
    UI --> MP
    MP --> KO
    AL --> KO
    KO --> EE
    EE --> TR --> T
    EE --> ML
    ML --> VS
    KO --> WR
    T --> NW
    WR --> ML
```

## 2. 唯一执行路径（内核）

```mermaid
sequenceDiagram
    participant M as main.py
    participant R as AgentOSRuntime
    participant ML as MemoryLayer
    participant W as WorldRuntime
    participant K as KernelOrchestrator
    participant E as ExecutionEngine
    participant T as ToolRouter

    M->>R: entry()
    R->>ML: build_context
    R->>W: step (纯状态)
    R->>K: build_plan
    K->>E: dispatch (唯一)
    E->>T: route tool
    T-->>E: result + trace
    E-->>R: output
    R->>W: apply_turn
    R->>ML: record_episode
```

## 3. 记忆治理写入路径

```mermaid
flowchart LR
    A["UI / API / CLI"] --> B["MemoryControl.authorize"]
    B --> C["build_kernel_plan"]
    C --> D["ExecutionEngine"]
    D --> E["execute_memory_op"]
    E --> F["MemoryLayer.apply_mutation"]
    F --> G["mutation_trace.jsonl"]
```

## 4. Phase 5 自主闭环

```mermaid
flowchart LR
    O["observe"] --> P["plan"]
    P --> A["act"]
    A --> R["reflect"]
    R --> O
```

每步 `AutonomousOSLoop` 仅调用 `AgentOSRuntime.entry()`，禁止第二 ExecutionEngine。

## 5. 部署与演示数据流

```mermaid
flowchart LR
    Browser["浏览器 :8787/app"] --> API["FastAPI agent_service"]
    API --> Runtime["AgentOSRuntime"]
    Runtime --> Mem["memory_db/ json"]
    API --> Stream["/api/desktop/stream MJPEG"]
    Stream --> Win["WSL 桌面捕获 Windows 主机"]
```
