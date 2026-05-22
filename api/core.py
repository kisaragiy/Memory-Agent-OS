# api/core.py

from agents.core import multi_agent_generate

def run_agent(session_id: str, user_input: str):
    response = multi_agent_generate(user_input)
    return response
