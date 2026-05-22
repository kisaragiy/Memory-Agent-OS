# Global dictionary to store protagonist for different sessions
PROTAGONIST = {
    "default": None
}

def set_protagonist(session_id="default", protagonist=None):
    if session_id not in PROTAGONIST:
        raise ValueError("Session ID must be pre-defined. Cannot create new session automatically.")
    PROTAGONIST[session_id] = protagonist

def get_protagonist(session_id="default"):
    return PROTAGONIST.get(session_id)
