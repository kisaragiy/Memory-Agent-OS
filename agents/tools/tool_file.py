# agents/tools/tool_file.py

from core.tools.tool_registry import register_tool

def run(input_text: str, filename: str = "output.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(input_text)
    return f"saved to {filename}"

# Register the tool automatically
register_tool("file_tool", run)
