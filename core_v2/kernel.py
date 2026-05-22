class Kernel:
    def __init__(self):
        self.memory = None
        self.agents = None

    def run(self, input_text):
        request_action(input_text)
