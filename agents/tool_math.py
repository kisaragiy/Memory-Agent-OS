from agents.tools.registry import register_tool


def calc(expression: str):
    try:
        return str(eval(expression))
    except Exception as e:
        return f"error: {e}"


register_tool(
    "calculator",
    calc,
    "执行数学计算，例如：2+2*10"
)
