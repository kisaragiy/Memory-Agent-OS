class WorldRenderer:

    def render(self, world_state):

        return {
            "video": self.render_video(world_state),
            "audio": self.render_audio(world_state),
            "subtitles": self.render_subtitles(world_state),
            "characters": self.render_characters(world_state),
            "emotion_map": self.render_emotions(world_state),
            "debug_state": world_state
        }

    def render_video(self, state):
        return {
            "shots": state.get("shots", []),
            "transitions": state.get("transitions", [])
        }

    def render_audio(self, state):
        return {
            "dialogue": state.get("dialogue", {}),
            "sound_effects": state.get("sound_effects", {})
        }

    def render_subtitles(self, state):
        return state.get("subtitles", [])

    def render_characters(self, state):
        characters = {}
        for character_name, character_data in state.get("characters", {}).items():
            characters[character_name] = {
                "status": character_data.get("status"),
                "position": character_data.get("position"),
                "expression": character_data.get("expression")
            }
        return characters

    def render_emotions(self, state):
        emotion_map = {}
        for character_name, emotions in state.get("emotions", {}).items():
            emotion_map[character_name] = {
                "happiness": emotions.get("happiness", 0.5),
                "sadness": emotions.get("sadness", 0.5),
                "anger": emotions.get("anger", 0.5),
                "fear": emotions.get("fear", 0.5)
            }
        return emotion_map
