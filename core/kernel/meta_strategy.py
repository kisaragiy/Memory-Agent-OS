from dataclasses import dataclass, field
from typing import List

@dataclass
class MetaStrategy:
    generator_pattern: str = None  # 如何生成策略
    selection_rule: str = None     # 如何选择策略结构
    success_rate: float = 0.5
    generated_strategies: List[dict] = field(default_factory=list)

class MetaStrategyLearner:

    def generate_strategy(self, task_type, context):
        # 从 context 中提取结构
        structure = self.extract_structure(context)
        strategy = {
            "pattern": structure,
            "task_type": task_type,
            "origin": "meta_generated"
        }
        return strategy

    def extract_structure(self, context):
        patterns = []
        if "分析" in str(context):
            patterns.append("decompose_problem")
        if "执行" in str(context):
            patterns.append("execute_steps")
        if "验证" in str(context):
            patterns.append("verify_result")
        return patterns

    def update_meta_strategy(self, meta, reward):
        meta.success_rate = (
            0.7 * meta.success_rate +
            0.3 * reward
        )
        # 成功 → 强化生成规则
        if reward > 0.8:
            meta.selection_rule = "expand_pattern_space"
