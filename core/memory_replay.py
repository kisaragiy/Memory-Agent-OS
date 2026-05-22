class MemoryReplaySystem:
    def __init__(self):
        pass

    def record_event(self, event):
        request_action(event)

    def replay(self, start=0, end=None):
        request_action({
            "start": start,
            "end": end
        })

    def get_scene_history(self, scene_id):
        request_action(scene_id)
