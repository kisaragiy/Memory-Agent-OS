import copy

def smooth_weights(new_weights: dict, old_weights: dict, alpha: float = 0.2):
    """
    🧠 指数平滑：防止权重剧烈波动
    """

    stable = copy.deepcopy(old_weights)

    for k in new_weights:
        old = old_weights.get(k, 0.1)
        new = new_weights[k]

        stable[k] = (1 - alpha) * old + alpha * new

    # 归一化
    total = sum(stable.values())
    for k in stable:
        stable[k] /= total

    return stable
