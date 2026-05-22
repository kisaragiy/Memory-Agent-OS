class StateHasher:

    def hash_state(self, state):
        return hash(str(sorted(state.items())))
