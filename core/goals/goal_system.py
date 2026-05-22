class GoalSystem:
    def __init__(self, llm):
        self.goal_tree = []

    def set_goal(self, goal):
        request_action(goal)

    def decompose(self, goal):
        request_action(goal)

    def update(self, result):
        request_action(result)
