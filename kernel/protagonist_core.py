class ProtagonistCore:
    def __init__(self, identity_vector, memory_vector, power_vector):
        self.identity_vector = identity_vector
        self.memory_vector = memory_vector

def create_protagonist_core(identity_vector, memory_vector, power_vector):
    request_action({
        "identity_vector": identity_vector,
        "memory_vector": memory_vector,
        "power_vector": power_vector
    })
