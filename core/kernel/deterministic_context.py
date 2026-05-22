class DeterministicContext:

    def __init__(self, input, kernel_state):
        self.input = input
        self.kernel_state_hash = hash(str(kernel_state))
        self.seed = self.generate_seed(input, kernel_state)

    def generate_seed(self, input, state):
        return hash(str(input) + str(state))
