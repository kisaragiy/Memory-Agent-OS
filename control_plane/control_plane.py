from .cluster_registry import ClusterRegistry
from .policy_governance import PolicyGovernance
from .telemetry_hub import TelemetryHub
from .resource_manager import ResourceManager

class GlobalScheduler:
    def __init__(self, registry):
        self.registry = registry

    def route(self, request):
        # select best cluster based on load + capability
        return min(
            self.registry.clusters,
            key=lambda c: c.load
        )

class ControlPlane:
    def __init__(self):
        self.registry = ClusterRegistry()
        self.scheduler = GlobalScheduler(self.registry)
        self.policy_engine = PolicyGovernance(self.registry)
        self.telemetry = TelemetryHub(self.registry)
        self.resource_manager = ResourceManager(self.registry)

    def route_request(self, request):
        cluster = self.scheduler.route(request)
        return cluster.handle(request)

    def auto_scale(self):
        for cluster in self.registry.clusters:
            if cluster.load > 0.8:
                self.resource_manager.scale_up(cluster)
            elif cluster.load < 0.2:
                self.resource_manager.scale_down(cluster)

    def enforce_consistency(self):
        self.policy_engine.sync_all_clusters()
