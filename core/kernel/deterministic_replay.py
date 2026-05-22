from core.kernel.deterministic_context import DeterministicContext

class DeterministicReplay:

    def replay(self, input, seed):
        context = DeterministicContext(input, seed)
        return self.runtime.handle_request(input)
