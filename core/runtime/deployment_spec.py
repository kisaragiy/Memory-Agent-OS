from typing import List

class DeploymentMode:
    MODES = [
        "RESEARCH",   # fully flexible
        "STABLE",     # bounded learning
        "RELEASE"     # no structural mutation
    ]

    def __init__(self, mode: str):
        if mode not in self.MODES:
            raise ValueError(f"Invalid deployment mode: {mode}")
        self.mode = mode

    def set_mode(self, mode: str):
        if mode not in self.MODES:
            raise ValueError(f"Invalid deployment mode: {mode}")
        self.mode = mode
