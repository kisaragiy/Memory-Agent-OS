# core/kernel/context_compressor.py

class ContextCompressor:

    def __init__(self, max_tokens=2000):
        self.max_tokens = max_tokens

    def compress(self, memory_bundle, current_input):
        """
        输入：
        - memory_bundle: MemoryManager 返回的记忆
        - current_input: 当前用户输入

        输出：
        - 压缩后的 context（dict）
        """

        episodic = memory_bundle.get("episodic", [])
        semantic = memory_bundle.get("semantic", [])
        goals = memory_bundle.get("goals", [])

        # 1️⃣ 过滤低价值记忆
        episodic = sorted(episodic, key=lambda x: x.get("importance", 0), reverse=True)[:5]
        semantic = sorted(semantic, key=lambda x: x.get("importance", 0), reverse=True)[:5]

        # 2️⃣ 构建压缩上下文
        context = {
            "current_input": current_input,
            "recent_events": episodic,
            "knowledge": semantic,
            "goals": goals[:3]
        }

        return context
