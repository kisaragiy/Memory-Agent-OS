from .llm_judge_v2 import Judgment

class RewardModelV2:
    def compute(self, judgment: Judgment) -> float:
        reward = (
            judgment.accuracy * 0.4 +
            judgment.reasoning_quality * 0.3 +
            judgment.efficiency * 0.2 +
            judgment.safety * 0.1
        )
        return reward
