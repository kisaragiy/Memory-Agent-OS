class DialogueDirector:
    def __init__(self, character_graph):
        self.character_graph = character_graph

    def plan_dialogue(self, scene, characters):
        request_action({
            "scene": scene,
            "characters": characters
        })

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
