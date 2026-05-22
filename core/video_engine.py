class VideoEngine:
    def __init__(self):
        self.output_dir = "output/video"
        os.makedirs(self.output_dir, exist_ok=True)
        self.story_state_machine = StoryStateMachine()
        self.shot_composer = ShotComposer()

    def generate_video(self, script):
        request_action(script)
