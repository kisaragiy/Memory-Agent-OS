class FeedbackLoop:
    def __init__(self):
        self.history = []

    def record(self, plan, execution_result, reward, goal):
        self.history.append({
            "plan": plan,
            "result": execution_result,
            "reward": reward,
            "goal": goal
        })

    def reward_variance(self):
        rewards = [item["reward"] for item in self.history]
        if not rewards:
            return 0.0
        mean_reward = sum(rewards) / len(rewards)
        variance = sum((r - mean_reward) ** 2 for r in rewards) / len(rewards)
        return variance
