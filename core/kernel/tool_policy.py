class ToolPolicy:

    def __init__(self):
        self.tool_scores = {}  # tool -> score

    def update(self, tool, reward, stabilizer):

        delta = reward - 0.5

        stable_delta = stabilizer.apply_momentum(tool, delta)

        lr = stabilizer.learning_rate

        self.tool_scores[tool] += lr * stable_delta
