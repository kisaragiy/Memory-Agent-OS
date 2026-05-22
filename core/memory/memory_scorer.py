class MemoryScorer:

    def score(self, content, memory_type, task_type):

        score = 0.5

        text = str(content)

        # identity（最高优先级）
        if memory_type == "identity":
            score += 0.4

        # goal（高价值）
        if memory_type == "goal":
            score += 0.3

        # 长信息（通常更重要）
        if len(text) > 20:
            score += 0.1

        # 关键词
        if any(k in text for k in ["重要", "必须", "记住"]):
            score += 0.2

        return min(score, 1.0)
