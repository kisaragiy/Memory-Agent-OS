class TimelineLock:
    active_world_id: str

    def __init__(self, active_world_id, active_story_id):
        self.active_world_id = active_world_id
        self.active_story_id = active_story_id

def lock_timeline(active_world_id, active_story_id):
    request_action({
        "active_world_id": active_world_id,
        "active_story_id": active_story_id
    })
