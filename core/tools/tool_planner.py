from core.kernel.system_guard import SystemGuard

class ToolPlanner:
    def __init__(self, tools, llm):
        self.tools = tools
        self.llm = llm
        self.system_guard = SystemGuard()

    def route(self, user_input, plan):
        self.system_guard.validate_call("UnifiedKernelRuntime")
        return f"[tool executed with plan: {plan}]"
