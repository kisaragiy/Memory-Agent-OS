import ollama

MODEL = "qwen3-writer:latest"


def generate_patch(file_path: str, instruction: str, code_context: str):
    prompt = f"""
你是代码修改代理。

目标文件：
{file_path}

当前代码：
{code_context}

修改要求：
{instruction}

请输出标准 diff patch 格式：

--- a/{file_path}
+++ b/{file_path}
@@
- 原代码
+ 修改后代码

只输出 patch，不要解释
"""

    res = ollama.generate(model=MODEL, prompt=prompt)
    return res["response"]
