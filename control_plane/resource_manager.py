class ResourceManager:
    def __init__(self, registry):
        self.registry = registry

    def scale_up(self, cluster):
        cluster.add_agent()

    def scale_down(self, cluster):
        cluster.remove_agent()
