from cluster.agent_cluster import AgentCluster

class DeploymentManager:
    def __init__(self, control_plane):
        self.control_plane = control_plane

    def deploy_cluster(self, config):
        cluster = AgentCluster(config)
        self.control_plane.register(cluster)
        return cluster
