class PersonaController:
    def __init__(self, llm):
        self.base_traits = {
            "林夏": ["理性", "好奇", "轻微情绪波动"]
        }

    def enforce(self, character, output):
        request_action({
            "character": character,
            "output": output
        })
