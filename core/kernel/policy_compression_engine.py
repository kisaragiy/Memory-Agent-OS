from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity
from dataclasses import dataclass, field

@dataclass
class StrategyNode:
    name: str
    success_rate: float = 0.0
    reward_history: List[float] = field(default_factory=list)
    parents: List['StrategyNode'] = field(default_factory=list)
    children: List['StrategyNode'] = field(default_factory=list)
    behavior_signature: list = field(default_factory=list)

class StrategySimilarity:

    def compute(self, a: StrategyNode, b: StrategyNode) -> float:
        return cosine_similarity([a.behavior_signature], [b.behavior_signature])[0][0]

class StrategyMerger:

    def merge(self, a: StrategyNode, b: StrategyNode) -> StrategyNode:
        merged_behavior = (a.behavior_signature + b.behavior_signature) / 2
        return StrategyNode(
            name=f"{a.name}_{b.name}_merged",
            behavior_signature=merged_behavior.tolist()
        )

class CompressionEvaluator:

    def average_performance(self, graph: 'StrategyGraph') -> float:
        if not graph.nodes:
            return 0.0
        total_success_rate = sum(node.success_rate for node in graph.nodes.values())
        return total_success_rate / len(graph.nodes)

    def strategy_count(self, graph: 'StrategyGraph') -> int:
        return len(graph.nodes)

    def score(self, graph: 'StrategyGraph') -> float:
        if not graph.nodes:
            return 0.0
        return (
            self.average_performance(graph) /
            self.strategy_count(graph)
        )

class RedundancyDetector:

    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold

    def find_redundant(self, graph: 'StrategyGraph') -> List[tuple]:
        redundant_pairs = []
        for a in graph.nodes.values():
            for b in graph.nodes.values():
                if a != b and self.compute_similarity(a, b) > self.similarity_threshold:
                    redundant_pairs.append((a, b))
        return redundant_pairs

    def compute_similarity(self, a: StrategyNode, b: StrategyNode) -> float:
        similarity_model = StrategySimilarity()
        return similarity_model.compute(a, b)

class StrategyAbstractor:

    def extract_common_pattern(self, strategies: List[StrategyNode]) -> list:
        if not strategies:
            return []
        common_signature = sum(strategy.behavior_signature for strategy in strategies) / len(strategies)
        return common_signature.tolist()

    def abstract(self, strategies: List[StrategyNode]) -> StrategyNode:
        return StrategyNode(
            name="abstracted_strategy",
            behavior_signature=self.extract_common_pattern(strategies)
        )

class PolicyCompressionEngine:

    def __init__(self):
        self.similarity = StrategySimilarity()
        self.merger = StrategyMerger()
        self.detector = RedundancyDetector()
        self.abstractor = StrategyAbstractor()

    def compress(self, graph: 'StrategyGraph') -> None:
        redundant_pairs = self.detector.find_redundant(graph)
        for a, b in redundant_pairs:
            merged = self.merger.merge(a, b)
            graph.add(merged)
            graph.remove(a)
            graph.remove(b)

    def abstract(self, graph: 'StrategyGraph') -> None:
        clusters = self.cluster_by_similarity(graph.nodes.values())
        for cluster in clusters:
            if len(cluster) > 3:
                abstracted_strategy = self.abstractor.abstract(cluster)
                graph.add(abstracted_strategy)

    def prune(self, graph: 'StrategyGraph') -> None:
        for node in list(graph.nodes.values()):
            if node.success_rate < 0.2:
                graph.remove(node)

    def cluster_by_similarity(self, nodes: List[StrategyNode]) -> List[List[StrategyNode]]:
        clusters = []
        visited = set()
        for node in nodes:
            if node not in visited:
                cluster = self.find_cluster(node, nodes)
                clusters.append(cluster)
                visited.update(cluster)
        return clusters

    def find_cluster(self, node: StrategyNode, nodes: List[StrategyNode]) -> List[StrategyNode]:
        cluster = [node]
        for other in nodes:
            if other != node and self.similarity.compute(node, other) > 0.85:
                cluster.append(other)
        return cluster
