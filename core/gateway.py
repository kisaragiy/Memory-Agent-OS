class AIGateway:
    def __init__(self):
        self.rag_engine = RAGEngine()

    def process_request(self, request):
        request_action(request)
