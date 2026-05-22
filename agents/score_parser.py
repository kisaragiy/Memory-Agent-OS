import ollama

TEXT_MODEL = "qwen3-writer:latest"


def call_llm(prompt: str) -> str:
    return ollama.generate(model=TEXT_MODEL, prompt=prompt)["response"]


def parse_scores(reflection: str) -> dict:
    """
    从反思中提取各 agent 表现评分
    """

    prompt = f"""
你是评分解析器。

根据反思内容，给每个agent一个表现评分：

范围：
-1.0（严重错误）
0.0（中性）
+1.0（表现很好）

---

反思内容：
{reflection}

---

输出JSON格式：
{
 "critic": 0.x,
 "memory": 0.x,
 "world": 0.x,
 "emotion": 0.x,
 "executor": 0.x
}
"""

    return eval(call_llm(prompt))  # 本地实验用（生产要换json parser）
