from core.kernel.system_guard import SystemGuard

class LongHorizonPlanner:
    def __init__(self, llm):
        self.llm = llm
        self.system_guard = SystemGuard()

    def plan(self, user_input, context):
        self.system_guard.validate_call("UnifiedKernelRuntime")
        return f"[plan based on {user_input}]"
