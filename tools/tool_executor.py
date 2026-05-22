# tools/tool_executor.py

import re
from tools.registry import get_tool


def try_tool_use(text: str) -> str:
    """
    Detect and execute tool calls in the text.
    """
    tool_pattern = r"\[\[TOOL:(\w+)\s+(.*?)\]\]"
    matches = re.findall(tool_pattern, text)

    for match in matches:
        tool_name, args = match
        tool_func = get_tool(tool_name)
        if tool_func:
            result = tool_func(args)
            text = text.replace(f"[[TOOL:{tool_name} {args}]]", str(result))

    return text
