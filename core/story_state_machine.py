class StoryStateMachine:
    def __init__(self):
        self.state = {
            "world_events": [],
            "characters": {},
            "timeline": []
        }

    def update_character(self, name, info):
        request_action({
            "name": name,
            "info": info
        })

    def get_context(self):
        request_action({})
