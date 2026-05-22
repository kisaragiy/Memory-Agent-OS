from typing import Dict

class TaskNode:
    def __init__(self, name, difficulty):
        self.name = name
        self.difficulty = difficulty  # 0.0 ~ 1.0
        self.success_rate = 0.0
        self.attempts = 0

class CurriculumGraph:
    def __init__(self):
        self.tasks = {}

    def add_task(self, task):
        self.tasks[task.name] = task

class DifficultyModel:
    def compute(self, task, performance):
        base = task.difficulty
        adjustment = 1.0 - performance.success_rate
        return min(1.0, base + adjustment * 0.5)

class CurriculumScheduler:
    def __init__(self, graph):
        self.graph = graph

    def select_task(self, agent_state):
        suitable_tasks = [
            t for t in self.graph.tasks.values()
            if abs(t.difficulty - agent_state.skill_level) < 0.2
        ]
        return max(suitable_tasks, key=lambda t: t.success_rate)

class AgentSkillModel:
    def __init__(self):
        self.skill_level = 0.5

    def update(self, reward_history):
        self.skill_level = sum(reward_history[-10:]) / 10 if len(reward_history) >= 10 else 0.5

class ProgressionController:
    def should_advance(self, agent_state):
        return agent_state.success_rate > 0.75

class CurriculumLearningEngine:
    def __init__(self):
        self.graph = CurriculumGraph()
        self.scheduler = CurriculumScheduler(self.graph)
        self.skill_model = AgentSkillModel()
        self.difficulty_model = DifficultyModel()

    def process_experience(self, task, reward):
        self.skill_model.update([reward])
        task.difficulty = self.difficulty_model.compute(task, self.skill_model)
        task.attempts += 1
        task.success_rate = reward
