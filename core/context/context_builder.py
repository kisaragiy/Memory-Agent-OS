class ContextBuilder:

    def __init__(self, repo_indexer, memory):

        self.repo = repo_indexer
        self.memory = memory


    def build(self, query):

        code_context = self.repo.search(query)
        memory_context = self.memory[-5:]

        return {
            "code": code_context,
            "memory": memory_context
        }
