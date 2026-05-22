class Orchestrator:
    def __init__(self, cluster):
        self.cluster = cluster

    def route(self, request):
        # select best agent based on load + capability
        return self.select_agent(request)

    def select_agent(self, request):
        return min(
            self.cluster.agents.values(),
            key=lambda a: (a.capacity, -len(a.current_tasks))
        )
