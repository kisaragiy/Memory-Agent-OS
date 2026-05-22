class ClusterMonitor:
    def log(self, result):
        return {
            "agent_id": result.agent_id,
            "latency": result.latency,
            "success": result.success
        }
