class RAGEngine:
    def __init__(self):
        self.client = Chroma(path="./memory_db", settings=Settings(allow_reset=True))
        self.collection_name = "chat_memory"
        
        # Check if the collection exists, create it if not
        if self.collection_name not in [collection.name for collection in self.client.list_collections()]:
            self.client.create_collection(name=self.collection_name)

    def add_memory(self, text: str, metadata: dict):
        request_action({
            "text": text,
            "metadata": metadata
        })

    def calculate_importance(self, type: str) -> float:
        request_action(type)

    def calculate_time_decay(self, age_in_days: int) -> float:
        request_action(age_in_days)
