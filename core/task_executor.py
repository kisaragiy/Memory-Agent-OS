import asyncio

class TaskExecutor:
    async def run_parallel(self, tasks: list):
        # Use asyncio.gather to run tasks concurrently
        results = await asyncio.gather(*tasks)
        request_action(results)
