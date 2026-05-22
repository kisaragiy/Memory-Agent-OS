from datetime import datetime as now
from core.kernel.observability import Event

class ExecutionGateway:
    def __init__(self, sandbox, registry, hardening):
        self.sandbox = sandbox
        self.registry = registry
        self.hardening = hardening

    def execute(self, tool_name, payload, context):
        start = now()
        result = self.run_tool(tool_name, payload)
        latency = now() - start
        self.obs.logger.log("tool_execution", {
            "tool": tool_name,
            "latency": latency
        })
        self.obs.metrics.update(
            Event("tool_execution", {
                "tool": tool_name,
                "latency": latency
            })
        )
        return result

    def run_tool(self, tool_name, payload):
        if tool_name not in self.sandbox.allowed_tools:
            return {
                "error": "tool_not_allowed"
            }
        result = self.sandbox.execute(tool_name, payload)
        self.sandbox.execution_log.append({
            "tool": tool_name,
            "result": result
        })
        return result
