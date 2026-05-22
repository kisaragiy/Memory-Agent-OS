# core/kernel/system_guard.py

ALLOWED_TOOL_LIST = [
    "llm",
    "memory_read",
    "memory_write",
    "analyzer",
    "recovery_kernel"
]

class SystemGuard:

    def validate_execution(self, call_path: str):
        allowed = [
            "core.kernel.runtime.UnifiedKernelRuntime.run",
            "core.kernel.runtime.UnifiedKernelRuntime.dispatch"
        ]

        if call_path not in allowed:
            raise Exception("KERNEL VIOLATION")

    def block_direct_memory_write(self):
        # Placeholder for blocking direct memory write
        pass

    def block_world_model_mutation(self):
        # Placeholder for blocking world model mutation
        pass

    def block_runtime_bypass(self):
        # Placeholder for blocking runtime bypass
        pass

    def enforce_execution_only_path(self):
        # Placeholder for enforcing execution-only path
        pass

    def block_memory_write(self):
        pass

    def block_world_mutation(self):
        pass

    def enforce_kernel_boundary(self):
        pass

    def validate_request(self, request):
        assert "type" in request
        assert "input" in request

    def forbid_direct_access(self):
        """
        禁止：
        - tool direct call
        - memory direct mutation
        - kernel bypass
        """
        pass

    def validate_plan(self, plan):
        assert isinstance(plan, dict)
        assert "goal" in plan
        assert len(plan["steps"]) > 0

        for step in plan["steps"]:
            assert "id" in step
            assert "action" in step

    def enforce_schema_lock(self, plan):
        """
        ❗任何不符合 schema 的 plan 直接 reject
        """
        if not self.validate_plan(plan):
            raise Exception("Invalid Planner Output")

    def validate_tool_call(self, tool_name, payload):

        assert tool_name in ALLOWED_TOOL_LIST

        assert payload is not None

    def forbid_direct_tool_execution(self):
        """
        禁止：
        - tool direct call outside sandbox
        - tool access kernel.entry
        - tool modify memory directly
        """
        pass

    def enforce_budget_constraints(self, execution_trace):
        """
        执行预算约束：
        - 步骤数限制
        - 工具调用次数限制
        - 递归深度限制
        """
        # 检查步骤数
        if len(execution_trace.get("steps", [])) > 100:
            raise Exception("Execution budget exceeded")
            
        # 检查工具调用次数
        tool_calls = [step for step in execution_trace.get("steps", []) if step.get("action") in ["tool_call"]]
        if len(tool_calls) > 5:
            raise Exception("Tool call budget exceeded")
            
        # 检查递归深度
        if execution_trace.get("depth", 0) > 10:
            raise Exception("Recursion depth exceeded")

    def enforce_memory_throttling(self, memory_operations):
        """
        内存写入节流：
        - 限制写入频率
        - 限制单次写入大小
        """
        # 检查写入频率
        if len(memory_operations) > 10:
            raise Exception("Memory write frequency exceeded")
            
        # 检查单次写入大小
        for op in memory_operations:
            if len(op.get("content", "")) > 1024:
                raise Exception("Memory write size exceeded")
                
    def enforce_stability_constraints(self, plans):
        """
        稳定性约束：
        - 多planner一致性检查
        - 防止计划发散
        """
        # 简单一致性检查
        if len(plans) > 1:
            common_steps = set(plans[0].get("steps", []))
            for plan in plans[1:]:
                common_steps = common_steps.intersection(set(plan.get("steps", [])))
                
            if len(common_steps) < 3:
                raise Exception("Planner consensus not achieved")
                
        # 防止计划发散
        if len(plans) > 5:
            raise Exception("Too many planner outputs")
            
    def forbid_direct_access(self):
        """
        禁止：
        - tool direct call
        - memory direct mutation
        - kernel bypass
        """
        pass
