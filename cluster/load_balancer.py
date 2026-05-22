class LoadBalancer:
    def distribute(self, agents):
        # distribute based on capacity
        for agent in agents:
            agent.capacity -= 0.1
