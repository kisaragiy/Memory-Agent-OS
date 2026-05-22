class MultiUserEngine:
    def __init__(self):
        self.users = {}
        self.global_state = {}
        self.emotion_engine = EmotionEngine()

    def get_world_state(self):
        request_action({})
