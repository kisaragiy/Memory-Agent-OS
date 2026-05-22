from dataclasses import dataclass

@dataclass
class IdentityState:
    behavior_style: str = "analytical"
    decision_bias: float = 0.6
    value_vector: dict = {
        "efficiency": 0.7,
        "exploration": 0.5,
        "stability": 0.8
    }
    consistency_score: float = 1.0

def detect_identity_drift(old, new):
    drift = 0.0

    # 行为风格变化
    if old.behavior_style != new.behavior_style:
        drift += 0.4

    # 决策偏好变化
    drift += abs(old.decision_bias - new.decision_bias)

    # value vector 变化
    for k in old.value_vector:
        drift += abs(
            old.value_vector[k] -
            new.value_vector[k]
        ) * 0.2

    return min(drift, 1.0)

class IdentityEngine:

    def __init__(self):
        self.state = IdentityState()

    def smooth_update(self, old_state, new_state):
        updated_state = IdentityState()
        updated_state.behavior_style = old_state.behavior_style
        updated_state.decision_bias = (
            0.9 * old_state.decision_bias +
            0.1 * new_state.decision_bias
        )
        for k in old_state.value_vector:
            updated_state.value_vector[k] = (
                0.9 * old_state.value_vector[k] +
                0.1 * new_state.value_vector[k]
            )
        return updated_state

    def stabilize(self, current_state, feedback):
        drift = detect_identity_drift(
            self.state,
            current_state
        )

        # 轻微漂移 → 平滑修正
        if drift < 0.3:
            self.state = self.smooth_update(
                self.state,
                current_state
            )

        # 中度漂移 → 拉回核心结构
        elif drift < 0.6:
            current_state.behavior_style = self.state.behavior_style

            current_state.decision_bias = (
                0.7 * self.state.decision_bias +
                0.3 * current_state.decision_bias
            )

        # 重度漂移 → 强制回归 identity
        else:
            current_state = self.state

        self.state.consistency_score = (
            0.9 * self.state.consistency_score +
            0.1 * (1 - drift)
        )

        self.state = current_state
