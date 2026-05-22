class GoalSelector:
    def __init__(self, motivation_engine):
        self.motivation = motivation_engine

    def select(self, goals, context):
        scored = [(goal, self.motivation.compute(goal, context)) for goal in goals]
        return max(scored, key=lambda x: x[1])[0]
