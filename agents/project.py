def init_project(session, user_input):
    if session["project"] is None:
        session["project"] = {
            "goal": user_input,
            "history": []
        }
