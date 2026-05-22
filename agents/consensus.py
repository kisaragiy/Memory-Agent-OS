import ollama
from agents.weights import get_task_weights

TEXT_MODEL = "qwen3-writer:latest"


def call_llm(prompt: str) -> str:
    return ollama.generate(model=TEXT_MODEL, prompt=prompt)["response"]


def weighted_consensus(inputs: dict, conflicts: str, task_type: str, adaptive_scores=None):

    AGENT_WEIGHTS = get_task_weights(task_type, adaptive_scores)

    scored_inputs = []

    for agent, content in inputs.items():
        weight = AGENT_WEIGHTS.get(agent, 0.1)

        scored_inputs.append(f"""
Agent: {agent}
Weight: {weight:.3f}
Output:
{content}
""")

    prompt = f"""
你是“任务感知型决策系统”。

当前任务类型：
{task_type}

规则：
- 不同任务权重不同
- 必须遵守任务结构
- conflict优先处理

---

冲突信息：
{conflicts}

---

{chr(10).join(scored_inputs)}

---

输出最终结果。
"""

    return call_llm(prompt).strip()
