def append_event(session_id="default", event=None):
    request_action({
        "session_id": session_id,
        "event": event
    })
