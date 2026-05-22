# agents/tools/registry.py

TOOLS = {}

def register(name, func):
    TOOLS[name] = func

def get_tool(name):
    return TOOLS.get(name)

# Automatically load tool modules
from . import tool_math
