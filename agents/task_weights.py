TASK_WEIGHT_MAP = {
    "creative": {
        "emotion": 0.35,
        "world": 0.25,
        "critic": 0.15,
        "memory": 0.15,
        "executor": 0.10
    },

    "code": {
        "critic": 0.40,
        "memory": 0.25,
        "executor": 0.25,
        "world": 0.05,
        "emotion": 0.05
    },

    "planning": {
        "planner": 0.35,
        "memory": 0.30,
        "world": 0.20,
        "critic": 0.10,
        "emotion": 0.05
    },

    "safe": {
        "critic": 0.50,
        "memory": 0.25,
        "world": 0.15,
        "executor": 0.05,
        "emotion": 0.05
    },

    "default": {
        "critic": 0.30,
        "memory": 0.25,
        "world": 0.20,
        "executor": 0.15,
        "emotion": 0.10
    }
}
