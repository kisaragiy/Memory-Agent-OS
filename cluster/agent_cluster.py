class AgentCluster:
    def __init__(self, config):
        self.agents = {}
        self.policy = None
        self.load = 0.0
        self.error_count = 0
        self.request_count = 0
        self.config = config

    def register(self, agent):
        self.agents[agent.id] = agent

    def get_agents(self):
        return self.agents.values()

    def update_policy(self, policy):
        self.policy = policy

    def add_agent(self):
        # Placeholder for adding an agent
        pass

    def remove_agent(self):
        # Placeholder for removing an agent
        pass

    def handle(self, request):
        # Placeholder for handling a request
        return {}

    def status(self):
        return {
            "agents": len(self.agents),
            "load": self.load,
            "error_count": self.error_count,
            "request_count": self.request_count
        }
