class RewardModel:

    def predict(self, goal_content):

        # Placeholder for prediction logic
        return {
            "correctness": 0.8,
            "relevance": 0.7,
            "completeness": 0.6,
            "clarity": 0.5
        }

    def compute(self, judge_result):

        return (
            0.4 * judge_result["correctness"] +
            0.3 * judge_result["relevance"] +
            0.2 * judge_result["completeness"] +
            0.1 * judge_result["clarity"]
        )

    def score_plan(self, plan, context):

        score = 0.5

        if plan.get("goal"):
            score += 0.2

        if "strategy_0" in plan.get("strategy", ""):
            score += 0.1  # baseline bias

        return score
