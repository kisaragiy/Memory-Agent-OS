# core/memory/memory_manager.py

from core.memory.memory_scorer import MemoryScorer
from core.memory.goal_manager import GoalManager

class MemoryManager:

    def __init__(self):
        self.scorer = MemoryScorer()
        self.goal_manager = GoalManager()

        self.episodic = []
        self.semantic = []

    def write_memory(self, text: str):
        importance = self.scorer.score(text)

        self.episodic.append({
            "text": text,
            "importance": importance
        })

        self.goal_manager.update(text)

    def retrieve(self, user_input):
        return {
            "episodic": sorted(self.episodic, key=lambda x: x["importance"], reverse=True),
            "semantic": self.semantic,
            "goals": self.goal_manager.get_goals()
        }
