def update_character_state(session_id, key, value):
    request_action({
        "session_id": session_id,
        "key": key,
        "value": value
    })
