# core/kernel/narrative_memory.py

class NarrativeMemory:

    def compress(self, narrative):

        """
        把长历史压缩成“剧情摘要”
        """

        return {
            "summary": narrative["theme"],
            "key_events": narrative["events"][-5:],
            "conflicts": len(narrative["conflicts"])
        }
