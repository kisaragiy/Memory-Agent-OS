class RollbackManager:

    def __init__(self):
        self.history = []

    def record(self, state):
        self.history.append(state)

    def rollback(self):
        if self.history:
            return self.history.pop()
        return None
