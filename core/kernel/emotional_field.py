# core/kernel/emotional_field.py

class EmotionalField:

    def __init__(self):
        self.field = {}

    def propagate(self, event):

        """
        情绪传播（不是单点情绪，是场）
        """

        emotion = "neutral"

        if "conflict" in str(event):
            emotion = "tension"

        if "cooperation" in str(event):
            emotion = "harmony"

        self.field[event.get("agent", "global")] = emotion

    def get_field(self):
        return self.field
