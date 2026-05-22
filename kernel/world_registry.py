class World:
    def __init__(self, world_id, ruleset):
        self.world_id = world_id

def register_world(world_id, ruleset):
    request_action({
        "world_id": world_id,
        "ruleset": ruleset
    })
