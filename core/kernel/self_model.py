class SelfModel:

    def __init__(self):

        self.capabilities = {
            "reasoning": 0.7,
            "coding": 0.8,
            "planning": 0.6,
            "tool_use": 0.5
        }

        self.limitations = {
            "long_context": 0.4,
            "uncertainty_handling": 0.5
        }

        self.task_performance = {}

    def update_capability(self, task_type, reward):

        if task_type not in self.capabilities:

            self.capabilities[task_type] = 0.5

        self.capabilities[task_type] = (
            0.8 * self.capabilities[task_type] +
            0.2 * reward
        )

    def log_performance(self, task_type, reward):

        if task_type not in self.task_performance:

            self.task_performance[task_type] = []

        self.task_performance[task_type].append(reward)

    def infer_capability(self, task_type):

        history = self.task_performance.get(task_type, [])

        if not history:

            return self.capabilities.get(task_type, 0.5)

        return sum(history[-10:]) / len(history[-10:])

    def detect_limitation(self):

        weak_points = []

        for k, v in self.capabilities.items():

            if v < 0.4:

                weak_points.append(k)

        return weak_points
