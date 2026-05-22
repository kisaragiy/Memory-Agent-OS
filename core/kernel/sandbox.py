# core/kernel/sandbox.py

from typing import Callable

TOOL_REGISTRY = {
    "llm": lambda payload: None,  # Placeholder for llm_tool
    "memory_read": lambda payload: None,  # Placeholder for memory_read_tool
    "memory_write": lambda payload: None,  # Placeholder for memory_write_tool
    "analyzer": lambda payload: None,  # Placeholder for analyzer_tool
    "recovery_kernel": lambda payload: None  # Placeholder for recovery_tool
}

class ToolSandbox:

    def __init__(self):
        self.allowed_tools = set()
        self.execution_log = []

    def register_tool(self, tool_name: str, tool_fn: Callable):
        self.allowed_tools.add(tool_name)
        TOOL_REGISTRY[tool_name] = tool_fn

    def execute(self, tool_name: str, payload) -> any:

        if tool_name not in self.allowed_tools:
            raise Exception(f"Tool not allowed: {tool_name}")

        # 🔒 强制隔离执行环境
        result = self._run_isolated(tool_name, payload)

        self.log(tool_name, payload, result)

        return result

    def _run_isolated(self, tool_name: str, payload) -> any:
        """
        ❗禁止 tool 访问 kernel / memory / runtime
        """

        # simulate isolation boundary
        if tool_name not in TOOL_REGISTRY:
            raise Exception(f"Tool not found: {tool_name}")

        return TOOL_REGISTRY[tool_name](payload)

    def log(self, tool: str, input_data: any, output: any):
        self.execution_log.append({
            "tool": tool,
            "input": input_data,
            "output": output
        })
