from dataclasses import dataclass, field
from typing import List

@dataclass
class StrategyNode:
    strategy: dict
    fitness: float = 0.5
    usage_count: int = 0
    mutation_history: List[dict] = field(default_factory=list)

class PolicyCompressor:

    def similarity(self, s1, s2):
        return (
            len(set(s1["pattern"]) & set(s2["pattern"])) /
            max(len(s1["pattern"]), 1)
        )

    def merge(self, s1, s2):
        merged = {
            "name": s1["name"] + "_merged",
            "pattern": list(set(
                s1["pattern"] + s2["pattern"]
            )),
            "origin": "compressed"
        }
        return merged

    def prune(self, graph):
        for node in list(graph.nodes.values()):
            if node.fitness < 0.3 and node.usage_count < 3:
                del graph.nodes[node.strategy["name"]]

    def distill(self, graph):
        core_strategies = []
        for node in graph.nodes.values():
            if node.fitness > 0.8:
                core_strategies.append(node.strategy)
        return core_strategies

    def compress(self, graph):
        nodes = list(graph.nodes.values())
        new_nodes = {}
        used = set()
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                s1, s2 = nodes[i], nodes[j]
                if self.similarity(s1.strategy, s2.strategy) > 0.8:
                    merged = self.merge(s1.strategy, s2.strategy)
                    new_nodes[merged["name"]] = merged
                    used.add(s1.strategy["name"])
                    used.add(s2.strategy["name"])
        for n in nodes:
            if n.strategy["name"] not in used:
                new_nodes[n.strategy["name"]] = n.strategy
        graph.nodes = new_nodes
