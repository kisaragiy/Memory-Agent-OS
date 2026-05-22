def evolve_system(reflection: str, agents: dict):
    """
    根据反思结果，修改系统行为
    """

    # 🧠 示例：这里只做“prompt进化”
    if "critic不够严格" in reflection:
        agents["critic"].system_prompt += "\n你必须更严格，减少宽松判断"

    if "memory冲突" in reflection:
        agents["memory"].system_prompt += "\n优先保证历史一致性"

    if "输出不稳定" in reflection:
        agents["consensus"].system_prompt += "\n必须优先解决冲突再输出"

    return agents
