from dataclasses import dataclass, field
from typing import List

@dataclass
class StrategySchema:
    name: str = None
    pattern: List[str] = field(default_factory=list)
    applicable_tasks: List[str] = field(default_factory=list)
    success_rate: float = 0.5
    instances: List[dict] = field(default_factory=list)

class StrategyGeneralizer:

    def generalize(self, strategy_instance, task_type):
        pattern = self.extract_pattern(strategy_instance)
        schema = StrategySchema()
        schema.name = f"gen_{task_type}_{len(self.store)}"
        schema.pattern = pattern
        schema.applicable_tasks.append(task_type)
        schema.instances.append(strategy_instance)
        return schema

    def extract_pattern(self, strategy):
        steps = strategy.get("pattern", [])
        abstract_steps = []
        for step in steps:
            if "代码" in step:
                abstract_steps.append("analyze_code")
            elif "对话" in step:
                abstract_steps.append("analyze_context")
            else:
                abstract_steps.append("process_step")
        return abstract_steps

class StrategyMemory:

    def __init__(self):
        self.schemas = {}

    def store(self, schema):
        if schema.name not in self.schemas:
            self.schemas[schema.name] = schema
        else:
            old = self.schemas[schema.name]
            old.success_rate = (0.7 * old.success_rate + 0.3 * schema.success_rate)

    def retrieve_best(self, task_type):
        candidates = []
        for schema in self.schemas.values():
            if task_type in schema.applicable_tasks:
                candidates.append(schema)
            elif len(set(schema.applicable_tasks)) > 1:
                candidates.append(schema)
        return sorted(candidates, key=lambda s: s.success_rate, reverse=True)[0] if candidates else None

    def update_strategy(self, schema_name, reward):
        if schema_name in self.schemas:
            schema = self.schemas[schema_name]
            schema.success_rate = (0.8 * schema.success_rate + 0.2 * reward)
            if reward > 0.8:
                schema.applicable_tasks.append("generalized")

    def store_generated(self, strategy):
        if strategy.get("origin") == "meta_generated":
            self.schemas[strategy["pattern"]] = strategy
