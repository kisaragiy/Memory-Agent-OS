# core/kernel/story_state_machine.py

class StoryStateMachine:

    def __init__(self):
        self.state = "intro"

    def transition(self, narrative):

        tension = narrative.get("tension", 0)

        if tension > 0.7:
            self.state = "climax"
        elif tension > 0.3:
            self.state = "rising"
        else:
            self.state = "intro"

        return self.state
