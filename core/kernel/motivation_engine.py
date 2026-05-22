class MotivationEngine:
    def compute(self, goal, context):
        importance = goal.priority
        expected_reward = context.get("expected_reward", 0.5)
        uncertainty = 1.0 - goal.completion
        return importance * expected_reward * uncertainty
