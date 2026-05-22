# core/planner/planner_optimizer.py

class PlannerOptimizer:

    def __init__(self):
        self.history = []

    def record(self, plan, success):
        self.history.append({
            "plan": plan,
            "success": success
        })

    def optimize(self, plan):
        """
        简化版：避免失败模式重复
        """

        failed_patterns = [
            h["plan"] for h in self.history if not h["success"]
        ]

        if plan in failed_patterns:
            # fallback策略
            return {
                "goal": plan.get("goal"),
                "steps": [{"action": "fallback_response"}]
            }

        return plan

    def learn(self, episode):

        score = episode["evaluation"]["score"]
        plan = episode["result"].get("plan")

        if not plan:
            return

        if score > 0.7:
            self.record(plan, True)
        else:
            self.record(plan, False)
