# agents/llm.py

import ollama

MODEL = "qwen3-writer:latest"  # 你之前用的模型


def call_llm(prompt: str) -> str:
    """
    🧠 统一LLM调用接口
    """
    response = ollama.generate(
        model=MODEL,
        prompt=prompt
    )

    return response["response"]
