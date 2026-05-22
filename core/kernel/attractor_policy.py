from dataclasses import dataclass, field
from typing import List

@dataclass
class Attractor:
    name: str
    strategies: List = field(default_factory=list)
    center_fitness: float = 0.5
    stability: float = 0.5

class AttractorSystem:

    def __init__(self):
        self.attractors = {}

    def assign(self, strategy_node):
        best = None
        best_score = 0

        for a in self.attractors.values():
            score = self.similarity(strategy_node, a)
            if score > best_score:
                best = a
                best_score = score

        if best:
            best.strategies.append(strategy_node)
        else:
            self.create_new_attractor(strategy_node)

    def create_new_attractor(self, strategy_node):
        attractor_name = f"attractor_{len(self.attractors)}"
        new_attractor = Attractor(name=attractor_name)
        new_attractor.strategies.append(strategy_node)
        self.attractors[attractor_name] = new_attractor

    def similarity(self, node, attractor):
        return (
            node.fitness * 0.4 +
            len(node.strategy.get("pattern", [])) * 0.2 +
            1.0 / (1 + len(attractor.strategies)) * 0.2 +
            node.usage_count * 0.2
        )

    def update_attractor(self, attractor, reward):
        attractor.center_fitness = (
            0.8 * attractor.center_fitness +
            0.2 * reward
        )
        attractor.stability = min(
            1.0,
            attractor.stability + 0.01
        )

    def compress(self):
        for a in self.attractors.values():
            if len(a.strategies) > 10:
                a.strategies = sorted(
                    a.strategies,
                    key=lambda s: s.fitness,
                    reverse=True
                )[:5]
