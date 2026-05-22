class WorldConstraintEngine:
    def __init__(self, cap_limit):
        self.cap_limit = cap_limit

    def clamp_power_vector(self, power_vector):
        request_action(power_vector)
