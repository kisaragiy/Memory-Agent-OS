from core.memory.memory_store import MemoryStore, MemoryItem
from core.memory.memory_scorer import MemoryScorer
from core.memory.memory_compressor import MemoryCompressor

class MemoryBrain:

    def __init__(self):
        self.store = MemoryStore()
        self.scorer = MemoryScorer()
        self.compressor = MemoryCompressor()

    def retrieve(self, task_type):
        items = [
            i for i in self.store.data
            if i.task_type == task_type
        ]

        items.sort(
            key=lambda x: x.importance * x.decay,
            reverse=True
        )

        return items[:10]

    def write(self, task_type, input, result):
        for content, mtype in [
            (input, "episodic"),
            (result, "episodic")
        ]:
            score = self.scorer.score(content, mtype, task_type)
            if score < 0.4:
                continue
            item = MemoryItem(content, mtype, task_type, score)
            self.store.add(item)

    def integrate_compressed(self, semantic_memories, task_type):
        for sm in semantic_memories:
            self.store.add(
                MemoryItem(
                    content=sm,
                    memory_type="semantic",
                    task_type=task_type,
                    score=0.9
                )
            )
