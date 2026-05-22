from typing import Dict, List

class HierarchicalPlanner:
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry

    def plan(self, context: Dict) -> Dict:
        # Placeholder for planning logic
        return {
            "task": context.get("input"),
            "strategy": "default_strategy",
            "actions": [
                {"type": "noop", "payload": {}}
            ]
        }
