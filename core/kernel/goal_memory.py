class GoalMemory:
    def __init__(self):
        self.active_goals = {}
        self.completed_goals = []

    def persist(self, goal):
        if goal.completion >= 1.0:
            self.completed_goals.append(goal)
        else:
            self.active_goals[goal.name] = goal

    def retrieve_active_goals(self):
        return list(self.active_goals.values())
