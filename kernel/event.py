class Event:
    def __init__(self, event_id, world_id, characters_involved, description, causal_links=None):
        self.event_id = event_id
        self.world_id = world_id
        self.characters_involved = characters_involved
        self.description = description

def create_event(event_id, world_id, characters_involved, description, causal_links=None):
    request_action({
        "event_id": event_id,
        "world_id": world_id,
        "characters_involved": characters_involved,
        "description": description,
        "causal_links": causal_links
    })
