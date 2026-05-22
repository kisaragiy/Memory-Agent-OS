from core.runtime.agent_os_runtime import AgentNode

class FailoverManager:
    def __init__(self, cluster):
        self.cluster = cluster

    def recover(self, agent):
        if agent.state == "failed":
            return self.spawn_new(agent)

    def spawn_new(self, agent):
        new_agent = AgentNode(id=f"{agent.id}_recovered")
        self.cluster.register(new_agent)
        return new_agent
