from core.kernel.system_guard import SystemGuard

class EmbeddingRAG:
    def __init__(self, chroma_client):
        self.chroma_client = chroma_client
        self.system_guard = SystemGuard()

    def query(self, query_text, top_k=5):
        self.system_guard.validate_call("UnifiedKernelRuntime")
        return f"[memory context for: {query_text}]"

    def embed(self, text):
        self.system_guard.validate_call("UnifiedKernelRuntime")
        # Existing implementation
        pass
