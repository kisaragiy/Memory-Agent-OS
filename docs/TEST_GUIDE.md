# Memory Agent OS — 测试指南

---

## 1. 测试目标

| 类型 | 目的 |
|------|------|
| 自动化回归 | 验证内核约束未被破坏 |
| 手工冒烟 | 发布前确认 UI/API 可用 |
| 集成验证 | 核心演示流程可重复 |

---

## 2. 自动化测试

```bash
cd AgentOSSystem
source .venv/bin/activate
python3 -m pytest tests/ -q
```

**期望**：全部通过，无 ERROR。

**覆盖范围（摘要）**：对齐策略、记忆治理、自主循环、Phase4 Guard、ModelPolicy 等。

---

## 3. 冒烟测试清单

### 3.1 服务启动

```bash
./scripts/start_production.sh
```

| 检查项 | 通过标准 |
|--------|----------|
| 进程监听 | `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8787/app/` 为 200 |
| API 文档 | `http://127.0.0.1:8787/docs` 可打开 |
| 前端资源 | `web/frontend/dist/index.html` 存在 |

### 3.2 API 单轮执行

```bash
curl -s -X POST http://127.0.0.1:8787/api/run \
  -H "Content-Type: application/json" \
  -d '{"message":"1+2","mode":"developer"}' | head -c 500
```

**通过标准**：响应含执行结果与 trace 相关字段。

### 3.3 记忆写入

```bash
curl -s -X POST http://127.0.0.1:8787/api/run \
  -H "Content-Type: application/json" \
  -d '{"message":"记住: 测试用户","mode":"developer"}' | head -c 800
```

**通过标准**：路由经 memory 通道，无 500 错误。

### 3.4 Phase5 自主会话（短步）

```bash
curl -s -X POST http://127.0.0.1:8787/api/autonomous/run \
  -H "Content-Type: application/json" \
  -d '{"goal":"echo hello","steps":2,"mode":"developer"}' | head -c 1000
```

**通过标准**：返回多步结构或会话数组；若 LLM/环境不可用，允许降级但需有 trace 说明。

### 3.5 桌面捕获（可选）

```bash
python3 scripts/verify_desktop_capture.py
```

**通过标准**：脚本报告捕获成功或给出明确环境提示。

---

## 4. UI 手工测试

在 **http://127.0.0.1:8787/app/** 开发者模式下：

| # | 操作 | 预期 |
|---|------|------|
| 1 | 输入 `1+2` | 结果 3，trace 含 code 路由 |
| 2 | 输入 `记住: 测试昵称` | 记忆成功提示或 trace |
| 3 | 勾选 Phase5，输入短目标 | 多步执行可见 |
| 4 | 打开桌面实况（若已配置） | 画面周期性刷新 |

---

## 5. 架构约束自检（发布前）

对照 `ARCHITECTURE_CONSTRAINTS.md`：

- [ ] 无新增第二 `ExecutionEngine`
- [ ] 显式 memory mutation 仅经 `execute_memory_op`
- [ ] WorldRuntime 无直接 tool/shell 调用
- [ ] UI 自动化经 `guarded_ui_action` + Guard

---

## 6. 缺陷记录模板

| 日期 | 场景 | 复现步骤 | 期望 | 实际 | 严重度 |
|------|------|----------|------|------|--------|
| | | | | | P0/P1/P2 |

---

## 7. 交付物清单

| 文件 | 说明 |
|------|------|
| `docs/ARCHITECTURE_DIAGRAM.md` | Mermaid 架构图源 |
| `docs/diagrams/*.png` | 脚本生成的位图（可选） |
| `docs/*.docx` | 运行 `generate_portfolio_docs.py` 生成（可选） |
