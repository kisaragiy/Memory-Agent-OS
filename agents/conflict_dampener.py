def dampen_conflicts(conflict_json: str) -> str:
    """
    🧠 根据冲突结果，映射系统稳定等级
    """

    if not conflict_json:
        return "LOW_CONFLICT"

    keywords_high = ["HIGH", "high"]
    keywords_med = ["MEDIUM", "medium"]

    if any(k in conflict_json for k in keywords_high):
        return "HIGH_CONFLICT"

    if any(k in conflict_json for k in keywords_med):
        return "MEDIUM_CONFLICT"

    return "LOW_CONFLICT"
