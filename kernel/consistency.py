def calculate_ccs(identity_vector, memory_vector, current_motivation):
    request_action({
        "identity_vector": identity_vector,
        "memory_vector": memory_vector,
        "current_motivation": current_motivation
    })
