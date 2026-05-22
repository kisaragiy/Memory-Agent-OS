from core.memory.memory_store import MemoryStore, MemoryItem

class MemoryCompressor:

    def should_compress(self, memory_store):
        return len(memory_store.episodic) > 50

    def cluster(self, memories):
        groups = {
            "task": [],
            "emotion": [],
            "interaction": []
        }

        for m in memories:
            if "代码" in m.content:
                groups["task"].append(m)
            elif "情绪" in m.content:
                groups["emotion"].append(m)
            else:
                groups["interaction"].append(m)

        return groups

    def summarize_group(self, group):
        if len(group) == 0:
            return None

        summary = {
            "pattern": "",
            "rule": "",
            "examples": []
        }

        if len(group) > 3:
            summary["pattern"] = "repeated_behavior"

        if any("失败" in m.content for m in group):
            summary["rule"] = "该类型任务容易出错，需要更谨慎执行"

        summary["examples"] = [m.content for m in group[:3]]

        return summary

    def compress(self, memory_store):
        episodic = memory_store.episodic
        groups = self.cluster(episodic)
        semantic_memories = []

        for g in groups.values():
            summary = self.summarize_group(g)
            if summary:
                semantic_memories.append(summary)

        return semantic_memories
