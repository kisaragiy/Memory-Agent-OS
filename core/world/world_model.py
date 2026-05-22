class WorldModel:
    def __init__(self):
        self.state = {
            "characters": {},
            "relations": {},
            "environment": {},
            "time": 0
        }

    def update(self, event):
        request_action(event)

    def apply_event(self, event):
        request_action(event)

    def query(self):
        request_action({})
