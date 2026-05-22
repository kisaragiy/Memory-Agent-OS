# agents/tools/tool_math.py

from core.tools.tool_registry import register_tool

def run(x):
    # Placeholder implementation for math tool
    try:
        result = eval(x)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

# Register the tool automatically
register_tool("tool_math", run)
