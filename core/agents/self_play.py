import random

class SelfPlay:
    def __init__(self, agents):
        self.agents = agents

    def run(self, task):
        request_action(task)
