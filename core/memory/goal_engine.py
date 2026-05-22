class Goal:
    def __init__(self, content, priority=0.5):
        self.content = content
        self.priority = priority
        self.persistence = 1.0
        self.decay = 0.99
        self.status = "active"

class GoalEngine:
    def __init__(self):
        self.goals = []

    def add_goal(self, content, priority=0.5):
        self.goals.append(Goal(content, priority))

    def update(self):
        for g in self.goals:
            if g.status != "active":
                continue
            g.persistence *= g.decay
            if g.persistence < 0.2:
                g.status = "expired"

def extract_goal(input_text):
    if "我要" in input_text or "目标" in input_text:
        return input_text
    return None
