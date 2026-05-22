from core.execution.reliable_loop import ReliableExecutor
from core.context.context_builder import ContextBuilder
from core.sandbox.sandbox import Sandbox
from core.kernel.system_guard import SystemGuard
from core.context.repo_indexer import RepoIndexer  # Added import for RepoIndexer

class CognitiveKernel:

    def __init__(self, memory_store, llm, retriever):

        self.memory = memory_store
        self.llm = llm
        self.retriever = retriever
        self.executor = ReliableExecutor(agent=self)
        self.context_builder = ContextBuilder(repo_indexer=RepoIndexer(), memory=memory_store)
        self.sandbox = Sandbox()
        self.guard = SystemGuard()


    def run(self, user_input):

        self.guard.enforce_call_chain("api.py")

        # 1. 构建上下文（统一入口）
        context = self.context_builder.build(user_input)

        # 2. 执行任务（唯一执行路径）
        result = self.executor.run({
            "input": user_input,
            "context": context
        })

        # 3. 可选 sandbox 执行
        if "code" in str(result):
            result = self.sandbox.run(result["code"])

        # 4. 记忆更新
        self.update_memory(user_input, result)

        return {
            'type': 'kernel_output',
            'data': result,
            'meta': {}
        }


    def select_memories(self, query):
        """
        Claude-like memory selection:
        - keyword overlap
        - time decay
        - role tagging (if exists)
        """
        memories = self.memory[-50:]

        scored = []
        for m in memories:
            score = self.simple_relevance_score(query, m)
            scored.append((score, m))

        scored.sort(reverse=True)
        result = [m for _, m in scored[:5]]
        return {
            'type': 'memory',
            'data': result,
            'meta': {}
        }


    def reason(self, input, memories):

        prompt = f"""
You are an AI reasoning system.

User: {input}

Relevant memory:
{memories}

Think step by step and generate response.
"""

        return self.llm(prompt)


    def reflect(self, input, output):

        prompt = f"""
Check if this response is correct and complete:

Input: {input}
Output: {output}

If good, return same.
If missing info, improve it.
"""

        return self.llm(prompt)


    def update_memory(self, input, output):

        compressed = f"{input} -> {output[:100]}"
        self.memory.append(compressed)

    def simple_relevance_score(self, query, memory):
        q_set = set(query.split())
        m_set = set(memory.split())

        overlap = len(q_set & m_set)

        return overlap

class MemoryOptimizer:

    def compress(self, memories):

        """
        Convert raw memories → semantic summaries
        """

        prompt = f"""
Summarize these memories into key facts:

{memories}

Return:
- user preferences
- stable facts
- emotional patterns
"""

        return self.llm(prompt)


    def update_long_term(self, memory, summary):
        # Store the summary in the memory store
        self.memory.append({
            "type": "semantic_memory",
            "content": summary
        })
