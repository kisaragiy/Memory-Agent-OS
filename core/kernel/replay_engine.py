# core/kernel/replay_engine.py

from core.kernel.tool_router import ToolRouter

class ReplayEngine:
    def __init__(self, tool_router: ToolRouter):
        self.tool_router = tool_router

    def replay(self, trace):
        results = []

        for step in trace:
            if step["type"] == "tool_call":
                result = self.tool_router.execute(
                    step["data"]["name"],
                    step["data"]["payload"]
                )
                results.append(result)

        return results
