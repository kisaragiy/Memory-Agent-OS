import ollama

TEXT_MODEL = "qwen3-writer:latest"


def call_llm(prompt: str) -> str:
    return ollama.generate(model=TEXT_MODEL, prompt=prompt)["response"]


def detect_conflicts(agent_outputs: dict) -> str:
    """
    🧠 多Agent冲突检测器
    输出必须结构化，便于后续稳定层处理
    """

    formatted = "\n\n".join([
        f"[{k}]\n{v}" for k, v in agent_outputs.items()
    ])

    prompt = f"""
你是“冲突检测系统（Conflict Detector）”。

你的任务：
1. 找出不同Agent输出之间的矛盾
2. 标记冲突点
3. 判断冲突等级

---

【Agent输出】
{formatted}

---

必须严格输出JSON格式：

{{
  "conflicts": [
    {{
      "agents": ["agent1", "agent2"],
      "issue": "冲突描述",
      "severity": "low|medium|high"
    }}
  ],
  "summary": "整体冲突总结",
  "level": "LOW|MEDIUM|HIGH"
}}

只输出JSON，不要解释，不要多余文本。
"""

    return call_llm(prompt)
