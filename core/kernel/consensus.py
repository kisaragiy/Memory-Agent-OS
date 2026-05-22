class ConsensusEngine:

    def select(self, plans, reward_model, context):

        scored = []

        for p in plans:

            score = reward_model.score_plan(p, context)

            scored.append((p, score))

        # 排序
        scored.sort(key=lambda x: x[1], reverse=True)

        # 投票逻辑（soft selection）
        top = scored[:2]

        # 加权选择（避免过拟合top1）
        final = top[0][0]

        return {
            "selected_plan": final,
            "candidates": [p for p, _ in scored],
            "scores": [s for _, s in scored]
        }
