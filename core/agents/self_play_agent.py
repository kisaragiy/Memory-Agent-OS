# core/agents/self_play_agent.py

from core.agents.curriculum_manager import CurriculumManager

class SelfPlayAgent:

    def __init__(self, runtime, evaluator):
        self.runtime = runtime
        self.evaluator = evaluator
        self.curriculum = CurriculumManager()

    def generate_task(self):
        tasks = self.curriculum.get_tasks()
        import random
        return random.choice(tasks)

    def run_episode(self):
        task = self.generate_task()

        result = self.runtime.run(task)

        score = self.evaluator.evaluate(task, result)

        episode = {
            "task": task,
            "result": result,
            "evaluation": score
        }

        self.curriculum.update(score["score"])

        return episode
