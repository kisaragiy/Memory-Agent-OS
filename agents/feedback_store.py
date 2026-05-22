AGENT_SCORE = {
    "critic": 0.0,
    "memory": 0.0,
    "world": 0.0,
    "emotion": 0.0,
    "executor": 0.0
}


def update_score(agent: str, score: float):
    """
    score: -1 ~ +1
    """
    if agent not in AGENT_SCORE:
        return

    # 🧠 指数滑动平均（稳定学习）
    AGENT_SCORE[agent] = AGENT_SCORE[agent] * 0.9 + score * 0.1


def get_scores():
    return AGENT_SCORE
