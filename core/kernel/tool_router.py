from core.tools.tool_registry import get_global_registry

class ToolRouter:
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry

    def execute(self, name: str, payload: dict) -> dict:
        if name not in self.tool_registry.list():
            return {
                "status": "error",
                "result": None,
                "error": f"Unregistered tool: {name}",
            }
        tool_instance = self.tool_registry.get_tool(name)
        result = tool_instance.execute(payload)
        if not isinstance(result, dict) or "status" not in result:
            return {
                "status": "error",
                "result": None,
                "error": "Tool contract violation: missing status",
            }
        return result
