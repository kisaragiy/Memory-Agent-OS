class ContextManager:

    def build_context(self, input, memory):

        context = {
            "input": input,
            "memory": memory
        }

        # 简单压缩（后续可升级）
        if len(memory) > 10:
            context["memory"] = memory[:10]

        return context
