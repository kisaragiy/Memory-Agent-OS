from typing import List
from .scoring import MemoryItem, MemoryScorer

class MemoryBrain:

    def __init__(self):
        self.memory_store: List[MemoryItem] = []

    def load_memory(self) -> List[MemoryItem]:
        # Placeholder for loading memory from a database or file
        return self.memory_store

    def retrieve(self, query, goal):
        all_memory = self.load_memory()
        scorer = MemoryScorer()

        scored = [
            (m, scorer.score(m, goal))
            for m in all_memory
        ]

        top_memory = sorted(scored, key=lambda x: x[1], reverse=True)[:5]

        return [m for m, score in top_memory]
