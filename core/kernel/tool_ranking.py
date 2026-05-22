class ToolPolicy:
    def __init__(self):
        self.tool_scores = {}

    def update_from_feedback(self, tool, reward):
        if reward < 0.4:
            self.tool_scores[tool] *= 0.9
        if reward > 0.8:
            self.tool_scores[tool] *= 1.1

    def get_tool_score(self, tool):
        return self.tool_scores.get(tool, 1.0)
