# tools/tool_math.py

import re

def math_tool(text: str) -> str:
    match = re.search(r"[0-9\+\-\*/\.\(\) ]+", text)
    if not match:
        return "0"

    expr = match.group(0)

    try:
        return str(eval(expr, {"__builtins__": None}, {}))
    except Exception as e:
        return f"error: {e}"


def register(register_tool):
    register_tool("math", math_tool)
