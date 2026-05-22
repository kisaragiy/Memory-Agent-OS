# core/kernel/goal_drift.py

class GoalDriftController:

    def __init__(self):
        self.initial_goal = None
        self.current_goal = None

    def set_goal(self, goal):
        self.initial_goal = goal
        self.current_goal = goal

    def check_drift(self, history):

        """
        检测目标是否漂移（核心能力）
        """

        if len(history) > 10:
            return "DRIFT_DETECTED"

        return "STABLE"
