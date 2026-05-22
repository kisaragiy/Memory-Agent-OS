from dataclasses import dataclass

@dataclass
class CognitiveState:
    reasoning_style: str = "analytical"
    decision_bias: float = 0.5
    memory_interpretation: str = "structured"
    stability_score: float = 0.5

class CognitiveStabilizer:

    def __init__(self):
        self.state = CognitiveState()

    def detect_drift(self, old_state, new_state):
        drift = 0

        if old_state.reasoning_style != new_state.reasoning_style:
            drift += 0.4

        if abs(old_state.decision_bias - new_state.decision_bias) > 0.2:
            drift += 0.3

        if old_state.memory_interpretation != new_state.memory_interpretation:
            drift += 0.3

        return drift

    def stabilize(self, state, feedback):
        drift = self.detect_drift(self.state, state)

        if drift > 0.5:
            # 强制回拉
            state.reasoning_style = self.state.reasoning_style

            state.decision_bias = (
                0.7 * self.state.decision_bias +
                0.3 * state.decision_bias
            )

        # 更新稳定性
        state.stability_score = (
            0.8 * state.stability_score +
            0.2 * (1 - drift)
        )

        self.state = state
