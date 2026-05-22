# core/kernel/memory/memory_scoring.py

from datetime import datetime, timedelta

class MemoryScorer:

    def score(self, memory_item, context):
        score = 0.0

        # 1. relevance（相关性）
        score += self.relevance(memory_item, context) * 0.4

        # 2. recency（时间衰减）
        score += self.recency(memory_item) * 0.2

        # 3. frequency（重复出现）
        score += self.frequency(memory_item) * 0.2

        # 4. information_gain（信息增益 / 新颖性）
        score += self.information_gain(memory_item) * 0.2

        return min(score, 1.0)

    def relevance(self, memory_item, context):
        # Placeholder for relevance calculation
        return 0.5

    def recency(self, memory_item):
        # Placeholder for recency calculation
        created_at = datetime.strptime(memory_item.get("created_at"), "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        age_in_days = (now - created_at).days
        return 1.0 / (age_in_days + 1)

    def frequency(self, memory_item):
        # Placeholder for frequency calculation
        return 0.5

    def information_gain(self, memory_item):
        # Placeholder for information gain calculation
        return 0.5
