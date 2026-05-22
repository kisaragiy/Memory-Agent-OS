class ToolUsageLog:
    def __init__(self):
        self.log = []

    def record(self, tool_name, input, output, success, reward):
        self.log.append({
            "tool_name": tool_name,
            "input": input,
            "output": output,
            "success": success,
            "reward": reward
        })

class ToolRewardModel:
    def score(self, tool_name, success, output):
        if not success:
            return -1.0

        if output is None:
            return -0.5

        # Placeholder for more complex scoring logic
        return 0.5

class ToolLearningEngine:
    def __init__(self):
        self.log = ToolUsageLog()
        self.reward_model = ToolRewardModel()

    def record_and_learn(self, tool_name, input, output, success):
        reward = self.reward_model.score(tool_name, success, output)
        self.log.record(tool_name, input, output, success, reward)

    def get_score(self, tool_name):
        # Placeholder for getting the average score of a tool
        return 0.5
