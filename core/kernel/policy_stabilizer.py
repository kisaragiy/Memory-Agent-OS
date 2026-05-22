class PolicyStabilizer:

    def __init__(self):
        self.learning_rate = 0.1
        self.momentum = {}
        self.history_window = 10

    def adaptive_lr(self, reward_variance):
        if reward_variance > 0.3:
            self.learning_rate *= 0.5  # Unstable -> slow down
        elif reward_variance < 0.1:
            self.learning_rate *= 1.05  # Stable -> slightly accelerate
        self.learning_rate = max(0.01, min(0.2, self.learning_rate))

    def apply_momentum(self, key, update):
        if key not in self.momentum:
            self.momentum[key] = update
            return update

        prev = self.momentum[key]

        # Smooth update
        smoothed = (
            0.7 * prev +
            0.3 * update
        )

        self.momentum[key] = smoothed

        return smoothed
