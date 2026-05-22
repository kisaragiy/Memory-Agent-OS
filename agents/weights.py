from agents.task_weights import TASK_WEIGHT_MAP


def get_task_weights(task_type: str, adaptive_scores=None):

    base = TASK_WEIGHT_MAP.get(task_type, TASK_WEIGHT_MAP["default"])

    # 🧠 可选：融合 C5 学习权重
    if adaptive_scores:
        for k in base:
            if k in adaptive_scores:
                base[k] = (base[k] + abs(adaptive_scores[k])) / 2

    # 归一化
    total = sum(base.values())
    return {k: v / total for k, v in base.items()}
