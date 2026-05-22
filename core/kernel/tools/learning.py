from dataclasses import dataclass

@dataclass
class ToolTrajectory:
    task: str
    tool: str
    success: bool
    latency: float
    output_quality: float

class RewardModel:
    def compute_reward(self, trajectory):
        reward = 0.0

        if trajectory.success:
            reward += 1.0
        else:
            reward -= 1.0

        # Output quality
        reward += trajectory.output_quality * 0.5

        # Latency penalty
        reward -= trajectory.latency * 0.1

        return reward

class ToolPolicyState:
    def __init__(self):
        self.tool_scores = {}   # {tool_name: weight}
        self.task_embeddings = {}  # Optional

class ToolPolicyLearner:
    def update(self, state, trajectory, reward):
        tool = trajectory.tool

        if tool not in state.tool_scores:
            state.tool_scores[tool] = 0.5

        # Simple reinforcement learning (bandit-like)
        state.tool_scores[tool] += 0.1 * reward

        # Limit range
        state.tool_scores[tool] = max(0.0, min(1.0, state.tool_scores[tool]))

class ToolPolicy:
    def select_tool(self, task, tools, state):
        best_tool = None
        best_score = -1

        for tool in tools:
            base_score = self.heuristic_score(task, tool)
            learned = state.tool_scores.get(tool.name, 0.5)
            final_score = 0.6 * base_score + 0.4 * learned

            if final_score > best_score:
                best_score = final_score
                best_tool = tool

        if best_score < 0.5:
            return None

        return best_tool

    def heuristic_score(self, task, tool):
        # Placeholder for heuristic scoring logic
        return 1.0
