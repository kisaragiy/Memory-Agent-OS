class ReliableExecutor:

    def __init__(self, agent, max_steps=10):
        self.agent = agent
        self.max_steps = max_steps


    def run(self, task):

        state = {
            "task": task,
            "step": 0,
            "history": [],
            "status": "running"
        }

        while state["step"] < self.max_steps:

            result = self.agent.act(state)

            state["history"].append(result)

            # ✅ done condition
            if self.is_done(result):
                state["status"] = "done"
                return result

            # ❗ failure detection
            if self.is_failed(result):
                result = self.retry(state, result)

            state["step"] += 1

        return {"status": "timeout", "history": state["history"]}


    def is_done(self, result):

        return "DONE" in str(result)


    def is_failed(self, result):

        return "error" in str(result).lower()


    def retry(self, state, last_result):

        prompt = f"""
Task failed. Retry with fix.

History:
{state["history"]}

Last error:
{last_result}
"""

        return self.agent.llm(prompt)
