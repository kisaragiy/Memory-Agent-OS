class PolicyGovernance:
    def __init__(self, registry):
        self.registry = registry

    def apply_global_policy(self, policy):
        for cluster in self.registry.clusters:
            cluster.update_policy(policy)

    def sync_all_clusters(self):
        base_policy = self.registry.clusters[0].policy
        for cluster in self.registry.clusters:
            cluster.policy = base_policy
