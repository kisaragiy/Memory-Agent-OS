# core/memory/goal_manager.py

class GoalManager:

    def __init__(self):
        self.goals = []

    def update(self, text):
        if any(k in text for k in ["我要", "我想", "目标"]):
            self.goals.append({
                "goal": text,
                "priority": 1.0
            })

    def get_goals(self):
        return sorted(self.goals, key=lambda x: x["priority"], reverse=True)
