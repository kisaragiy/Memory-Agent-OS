PLAN_SCHEMA_KEYS = {"task", "strategy", "task_type", "actions"}
ACTION_SCHEMA_KEYS = {"type", "name", "payload"}

TOOL_ACTION_SCHEMA = {
    "name": str,
    "payload": {
        "code": (str, type(None)),
        "input": (str, type(None)),
        "args": dict
    }
}
