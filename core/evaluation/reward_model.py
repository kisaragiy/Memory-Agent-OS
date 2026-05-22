# core/evaluation/reward_model.py

class RewardModel:

    def compute(self, llm_score, heuristic_score):
        """
        融合评分（防止 LLM 自嗨）
        """

        # LLM评分权重
        w1 = 0.6

        # 规则评分权重
        w2 = 0.4

        reward = w1 * llm_score + w2 * heuristic_score

        return reward
