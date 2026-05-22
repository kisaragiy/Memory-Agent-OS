def enforce(world_id):
    request_action(world_id)

def fork(world_id, reason):
    request_action({
        "world_id": world_id,
        "reason": reason
    })
