from control_plane.global_scheduler import GlobalScheduler
from control_plane.cluster_registry import ClusterRegistry

class APIGateway:
    def __init__(self, auth_system):
        self.auth = auth_system
        self.router = GlobalScheduler(ClusterRegistry())

    def handle_request(self, request):
        self.auth.validate(request)
        routed = self.router.route(request)
        return routed.handle(request)
