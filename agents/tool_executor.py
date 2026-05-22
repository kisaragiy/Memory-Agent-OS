import json
from agents.tools.registry import get_tool


def try_tool_use(text: str):
    """
    检测模型是否要调用工具
    """

    if "TOOL_CALL" not in text:
        return None

    try:
        payload = text.split("TOOL_CALL:")[1].strip()
        data = json.loads(payload)

        tool_name = data["tool"]
        args = data.get("args", {})

        tool = get_tool(tool_name)

        if not tool:
            return f"[Tool Error] tool not found: {tool_name}"

        result = tool["func"](**args)

        return f"[Tool Result] {result}"

    except Exception as e:
        return f"[Tool Error] {e}"
