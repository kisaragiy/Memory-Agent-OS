class ExecutionOrderLock:

    def enforce(self, pipeline):
        canonical_order = [
            "identity_check",
            "memory_retrieval",
            "planning",
            "execution",
            "reflection"
        ]
        return canonical_order
