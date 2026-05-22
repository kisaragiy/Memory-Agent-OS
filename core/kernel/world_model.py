# core/kernel/world_model.py

class WorldStateModel:

    def __init__(self):
        self.state = {
            "entities": {},
            "relations": {},
            "timeline": []
        }

    def update(self, event):
        """
        更新世界状态（不是memory，是世界状态）
        """

        self.state["timeline"].append(event)

        if "agent" in event:
            self.state["entities"][event["agent"]] = event

    def snapshot(self):
        return self.state


class CausalEngine:

    def predict(self, state, action):

        """
        简化因果模拟（不是ML推理，是规则模拟）
        """

        outcome = {}

        if "conflict" in action:
            outcome["risk"] = "high"

        if "cooperate" in action:
            outcome["risk"] = "low"

        return outcome
