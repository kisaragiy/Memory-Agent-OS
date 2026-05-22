class ExecutionTrace:
    def __init__(self):
        self.trace = []

    def log(self, step_type, data):
        self.trace.append({"step_type": step_type, "data": data})

    def export(self):
        return self.trace
