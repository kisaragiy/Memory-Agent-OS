# core/kernel/stability_convergence.py

class StabilityConvergenceKernel:
    def __init__(self):
        self.max_steps = 8
        self.max_tool_calls = 3
        self.max_depth = 5
        self.execution_budget = 100  # Default budget for execution steps
        self.recursion_depth = 0

    def clamp_plan(self, plan):
        """限制 plan 长度 / 深度 / 分支"""
        # 实现 plan 截断逻辑
        # 限制步骤数量
        if len(plan.get("steps", [])) > self.max_steps:
            plan["steps"] = plan["steps"][:self.max_steps]
        
        # 限制工具调用次数
        tool_calls = [step for step in plan.get("steps", []) if step.get("action") in ["tool_call"]]
        if len(tool_calls) > self.max_tool_calls:
            plan["steps"] = [step for step in plan["steps"] if not (step.get("action") in ["tool_call"])]
        
        # 限制深度
        if plan.get("depth", 0) > self.max_depth:
            plan["depth"] = self.max_depth
            
        return plan

    def enforce_tool_budget(self, tool_calls):
        """限制工具调用次数"""
        # 实现工具调用预算控制逻辑
        if len(tool_calls) > self.max_tool_calls:
            return tool_calls[:self.max_tool_calls]
        return tool_calls

    def validate_execution(self, execution_trace):
        """判断是否允许继续执行"""
        # 实现执行验证逻辑
        # 检查步骤数是否超过预算
        if len(execution_trace.get("steps", [])) > self.execution_budget:
            return "BLOCK"
        
        # 检查递归深度
        if self.recursion_depth > self.max_depth:
            return "BLOCK"
            
        # 检查工具调用次数
        tool_calls = [step for step in execution_trace.get("steps", []) if step.get("action") in ["tool_call"]]
        if len(tool_calls) > self.max_tool_calls:
            return "RISKY"
            
        return "SAFE"

    def consensus_check(self, plans):
        """多planner一致性检查"""
        # 实现一致性检查逻辑
        # 简单实现：取所有plan的交集
        if not plans:
            return {}
            
        common_steps = set(plans[0].get("steps", []))
        for plan in plans[1:]:
            common_steps = common_steps.intersection(set(plan.get("steps", [])))
            
        return {"steps": list(common_steps)}
