class BranchNode:
    def __init__(self, world_id, event_id, parent_id=None, branch_reason=""):
        self.world_id = world_id
        self.event_id = event_id
        self.parent_id = parent_id
        self.branch_reason = branch_reason

def create_branch_node(world_id, event_id, parent_id=None, branch_reason=""):
    request_action({
        "world_id": world_id,
        "event_id": event_id,
        "parent_id": parent_id,
        "branch_reason": branch_reason
    })
