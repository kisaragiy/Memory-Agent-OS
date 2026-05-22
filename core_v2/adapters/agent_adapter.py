class AgentAdapter:
    def __init__(self):
        self.planner = PlannerBrain()
        self.dialogue_director = DialogueDirector(CharacterGraph())

    def simple_rule_based_planner(self, user_input: str):
        request_action(user_input)

    def determine_emotion(self, context, scene):
        request_action({
            "context": context,
            "scene": scene
        })

    def determine_intent(self, context, scene):
        request_action({
            "context": context,
            "scene": scene
        })

    def generate_content(self, scene, character, emotion):
        request_action({
            "scene": scene,
            "character": character,
            "emotion": emotion
        })

    def set_emotion(self, character, emotion, intensity=1.0):
        request_action({
            "character": character,
            "emotion": emotion,
            "intensity": intensity
        })
