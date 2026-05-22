from typing import Dict

class StrategyPool:
    def __init__(self):
        self.policies = {}

class PolicyOptimizer:
    def update(self, policy, reward):
        pass  # Placeholder for actual implementation

class Goal:
    def __init__(self, name, priority):
        self.name = name
        self.priority = priority

class PolicyOptimizationEngine:
    def __init__(self, motivation_engine, strategy_graph, attractor_pool):
        self.pool = StrategyPool()
        self.optimizer = PolicyOptimizer()
        self.motivation = motivation_engine
        self.strategy_graph = strategy_graph
        self.attractor_pool = attractor_pool

    def select_strategy(self, context):
        best_attractor = max(
            self.attractor_pool.attractors,
            key=lambda a: a.center.stability_score
        )
        return best_attractor.center

    def process_experience(self, trace: Dict, reward: float, goal: Goal) -> Dict:
        goal.priority += reward * 0.1
        strategy_name = trace.get("strategy", "")
        node = self.strategy_graph.get_node(strategy_name)
        if node:
            self.optimizer.update(node, reward)
        return {
            "goal_updated": goal.name,
            "new_priority": goal.priority
        }
