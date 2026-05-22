class DeterminismController:

    def __init__(self):
        self.fixed_seed = 42

    def lock_seed(self, context):
        return context.seed % self.fixed_seed
