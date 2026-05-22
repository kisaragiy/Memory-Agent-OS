# core/kernel/recovery.py

class ExecutionError(Exception):
    pass

class ToolExecutionError(ExecutionError):
    pass

class PlanningError(ExecutionError):
    pass

class ValidationError(ExecutionError):
    pass

class MemoryError(ExecutionError):
    pass

class RecoveryStrategy:

    def handle(self, error, context):

        if isinstance(error, ToolExecutionError):
            return self.retry_tool(context)

        if isinstance(error, PlanningError):
            return self.replan(context)

        if isinstance(error, ValidationError):
            return self.fix_input(context)

        return self.fallback(context)

class RetryPolicy:

    def __init__(self):
        self.max_retries = 2

    def should_retry(self, context):
        return context.get("retry_count", 0) < self.max_retries

class PlanRepair:

    def repair(self, plan, error):

        # 简单策略：降级复杂度
        if "multi_step" in plan:
            return {"task": plan["task"], "mode": "simple"}

        return plan

class FallbackHandler:

    def handle(self, context):

        return {
            "status": "fallback",
            "message": "系统已自动降级处理该请求"
        }

class RecoveryKernel:

    def __init__(self):
        self.strategy = RecoveryStrategy()
        self.retry_policy = RetryPolicy()
        self.plan_repair = PlanRepair()
        self.fallback = FallbackHandler()

    def execute(self, func, context):

        try:
            return func()

        except Exception as e:

            context["error"] = str(e)
            context["retry_count"] = context.get("retry_count", 0) + 1

            # 1. 判断是否重试
            if self.retry_policy.should_retry(context):
                repaired = self.plan_repair.repair(context.get("plan"), e)
                context["plan"] = repaired

                return self.execute(func, context)

            # 2. fallback
            return self.fallback.handle(context)
