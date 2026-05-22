def evaluate_execution(result, goal):
    score = 0.5

    if result is None:
        return 0.0

    if "error" in str(result):
        score -= 0.3

    if goal and goal in str(result):
        score += 0.3

    if len(str(result)) > 20:
        score += 0.1

    return max(0.0, min(score, 1.0))
