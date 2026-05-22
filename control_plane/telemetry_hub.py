class TelemetryHub:
    def __init__(self, registry):
        self.registry = registry

    def collect(self):
        return {
            "clusters": self.snapshot_clusters(),
            "latency": self.avg_latency(),
            "error_rate": self.error_rate(),
            "utilization": self.utilization()
        }

    def snapshot_clusters(self):
        return [cluster.status() for cluster in self.registry.clusters]

    def avg_latency(self):
        total_latency = sum(cluster.latency for cluster in self.registry.clusters)
        return total_latency / len(self.registry.clusters) if self.registry.clusters else 0

    def error_rate(self):
        total_errors = sum(cluster.error_count for cluster in self.registry.clusters)
        total_requests = sum(cluster.request_count for cluster in self.registry.clusters)
        return total_errors / total_requests if total_requests > 0 else 0

    def utilization(self):
        total_capacity = sum(cluster.capacity for cluster in self.registry.clusters)
        total_load = sum(cluster.load for cluster in self.registry.clusters)
        return total_load / total_capacity if total_capacity > 0 else 0
