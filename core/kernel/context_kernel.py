# core/kernel/context_kernel.py

class ContextKernel:

    def __init__(self, memory):
        self.memory = memory
        self.max_tokens = 500  # 控制上下文大小

    def build_context(self, user_input: str):
        """
        构建最终给 LLM 的上下文
        """

        # 1. 当前输入
        current = user_input

        # 2. 记忆检索
        memory_context = self.memory.get_context()

        # 3. 拼接
        context = f"""
        [当前问题]
        {current}

        [关键记忆]
        {memory_context}
        """

        return self.compress(context)

    def compress(self, text: str):
        """
        分层压缩策略
        """
        sections = {
            "input": "",
            "memory": "",
            "history": ""
        }

        # Split the text into sections
        lines = text.split('\n')
        section = None
        for line in lines:
            if line.startswith("[当前问题]"):
                section = "input"
            elif line.startswith("[关键记忆]"):
                section = "memory"
            elif line.startswith("[最近上下文]"):
                section = "history"
            else:
                if section:
                    sections[section] += line + "\n"

        # Compress each section
        while len(text) > self.max_tokens:
            if sections["history"]:
                sections["history"] = ""
            elif sections["memory"]:
                sections["memory"] = ""
            else:
                break

            text = f"""
            [当前问题]
            {sections["input"]}

            [关键记忆]
            {sections["memory"]}

            [最近上下文]
            {sections["history"]}
            """

        return text.strip()
