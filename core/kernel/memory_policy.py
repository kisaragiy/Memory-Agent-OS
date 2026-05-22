# core/kernel/memory_policy.py

class MemorySelectionPolicy:

    def __init__(self):
        self.memory_bank = []

    def score_memory(self, query, memory_item):
        """
        非RAG向量检索，而是启发式认知评分：
        - 语义相关性（简单关键词）
        - 时间衰减
        - 任务一致性
        """
        score = 0

        if any(w in memory_item for w in query.split()):
            score += 1.0

        # 最近记忆权重
        score += 0.1  # placeholder decay

        return score

    def select(self, query, memories, top_k=5):
        scored = [(m, self.score_memory(query, m)) for m in memories]
        scored.sort(key=lambda x: x[1], reverse=True)
        result = [m for m, _ in scored[:top_k]]
        return {
            'type': 'memory',
            'data': result,
            'meta': {}
        }
