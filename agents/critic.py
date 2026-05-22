# agents/critic.py

def critic(draft: str, baseline: str = None) -> dict:
    """
    🧠 v2.5 Critic（支持 baseline 对比）
    返回：
    {
        "content": str,
        "score": int,
        "meta": dict
    }
    """

    # 默认反馈
    feedback_text = ""
    score = 7

    if baseline:
        # 简单对比逻辑（长度 + 内容）
        if len(draft) > len(baseline):
            score = 8
            feedback_text = "Draft is more detailed than baseline."
        elif len(draft) < len(baseline):
            score = 5
            feedback_text = "Draft is less detailed than baseline. Improve it."
        else:
            score = 6
            feedback_text = "Draft is similar to baseline. Consider improving clarity."

    else:
        feedback_text = "General quality acceptable."

    print(f"[CRITIC SCORE] {score}")
    print(f"[CRITIC FEEDBACK] {feedback_text}")

    return {
        "content": feedback_text,
        "score": score,
        "meta": {}
    }
