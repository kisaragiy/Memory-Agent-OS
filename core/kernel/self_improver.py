class SelfImprover:

    def __init__(self):
        self.history = {}  # task_type -> list

    def record(self, task_type, plan, tool, reward):

        if task_type not in self.history:
            self.history[task_type] = []

        self.history[task_type].append({
            "plan": plan,
            "tool": tool,
            "reward": reward
        })

    def analyze(self, task_type):

        data = self.history.get(task_type, [])

        stats = {}

        for h in data:
            t = h["tool"]
            if t not in stats:
                stats[t] = []
            stats[t].append(h["reward"])

        return {
            k: sum(v)/len(v)
            for k, v in stats.items()
        }
