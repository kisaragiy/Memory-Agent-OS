from dataclasses import dataclass

@dataclass
class MemoryItem:
    id: str
    content: str
    timestamp: float
    importance: float
    goal_relevance: float
    emotional_weight: float
    access_count: int
    decay_factor: float

class MemoryScorer:

    def score(self, memory, current_goal):
        return (
            self.goal_alignment(memory, current_goal) * 0.4 +
            self.recency(memory) * 0.15 +
            self.emotion(memory) * 0.15 +
            self.frequency(memory) * 0.1 +
            self.causal_link(memory, current_goal) * 0.2
        )

    def goal_alignment(self, memory, goal):
        if not goal:
            return 0.2
        # Placeholder for similarity function
        return 0.5

    def recency(self, memory):
        from time import time
        current_time = time()
        decay_factor = 0.99  # Example decay factor
        return (current_time - memory.timestamp) * decay_factor

    def emotion(self, memory):
        return memory.emotional_weight

    def frequency(self, memory):
        import math
        return math.log(memory.access_count + 1)

    def causal_link(self, memory, goal):
        # Placeholder for weak causal match function
        return 0.3
