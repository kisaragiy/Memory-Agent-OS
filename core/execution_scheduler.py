import asyncio

class ExecutionScheduler:
    def __init__(self):
        self.queue = []
        self.running = False
        self.max_workers = 2
        self.mode = "AI"  # or "GAME"

    async def run(self):
        request_action({})
