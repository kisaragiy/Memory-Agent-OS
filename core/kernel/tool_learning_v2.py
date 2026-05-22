from typing import Dict

class Tool:
    def __init__(self, name):
        self.name = name
        self.success_rate = 0.0
        self.latency = 0.0
        self.utility_score = 0.0

class ToolUtilityModel:
    def compute(self, tool, context, goal):
        expected_gain = context.get("expected_gain", 0.5)
        cost = tool.latency
        risk = 1.0 - tool.success_rate
        goal_factor = goal.priority
        return (expected_gain * goal_factor) - cost - risk

class ToolPolicy:
    def __init__(self):
        self.utility_model = ToolUtilityModel()

    def select(self, tools, context, goal):
        scored = []
        for tool in tools:
            score = self.utility_model.compute(tool, context, goal)
            scored.append((tool, score))
        scored.append(("NO_TOOL", context.get("baseline_reward", 0.3)))
        return max(scored, key=lambda x: x[1])[0]

class UncertaintyGate:
    def should_use_tool(self, context):
        return context.get("uncertainty", 0.0) > 0.4

class ToolMemory:
    def __init__(self):
        self.usage_history = []

    def log(self, tool, reward):
        self.usage_history.append({
            "tool": tool,
            "reward": reward
        })

class ToolRewardAttribution:
    def assign(self, trace, reward):
        return trace.get("tool_used", "NO_TOOL"), reward

class ToolLearningEngine:
    def __init__(self, registry):
        self.utility_model = ToolUtilityModel()
        self.policy = ToolPolicy()
        self.memory = ToolMemory()
        self.gate = UncertaintyGate()
        self.registry = registry

    def decide(self, context, goal):
        if not self.gate.should_use_tool(context):
            return "NO_TOOL"
        return self.policy.select(self.registry.tools.values(), context, goal)
