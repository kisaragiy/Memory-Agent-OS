class ClusterRegistry:
    def __init__(self):
        self.clusters = []

    def register(self, cluster):
        self.clusters.append(cluster)

    def list_clusters(self):
        return self.clusters
