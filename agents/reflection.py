import ollama

TEXT_MODEL = "qwen3-writer:latest"


def call_llm(prompt: str) -> str:
    return ollama.generate(model=TEXT_MODEL, prompt=prompt)["response"]


def reflection_agent(user_input: str, output: str, critic: str, conflicts: str) -> str:

    prompt = f"""
你是“系统反思器（Reflection Engine）”。

你的任务：
- 分析这次系统输出的质量问题
- 找出失败原因
- 提出系统级改进建议（不是内容改进）

---

【用户输入】
{user_input}

【最终输出】
{output}

【审查反馈】
{critic}

【冲突信息】
{conflicts}

---

输出格式：
1. 问题总结
2. 系统缺陷（重点）
3. 改进建议（必须具体到agent或机制）
"""

    return call_llm(prompt).strip()
