from typing import Dict
import json

from core.tools.tool_registry import get_global_registry
from core.protocol.plan_compiler import PlanCompiler
from core.control.model_policy import ModelPolicy
from core.llm.client import invoke_llm, strip_markdown_fences


class StrategyGraph:
    def select_best(self, task_type):
        return {"strategy": "default_strategy", "risk_level": 0}


class HierarchicalPlanner:
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry
        self.strategy_graph = StrategyGraph()

    def plan(self, context: Dict) -> str:
        task_type = self._infer_task_type(context)
        strategy = self.strategy_graph.select_best(task_type)
        user_input = context.get("input", "")
        intent = self.classify_intent(user_input)

        spec = ModelPolicy.build_planner_invocation(context)
        generated_code = strip_markdown_fences(invoke_llm(spec))

        return json.dumps(
            {
                "task": user_input,
                "task_type": task_type,
                "intent": intent,
                "strategy": strategy["strategy"],
                "actions": [
                    {
                        "type": "tool",
                        "name": "execute_code",
                        "payload": {"code": generated_code},
                    }
                ],
                "_meta": {
                    "model_policy": spec.to_dict(),
                    "routing": "execute_code",
                },
            }
        )

    def _infer_task_type(self, context):
        text = context.get("input", "")
        if "API" in text or "接口" in text:
            return "api_generation"
        if "bug" in text or "错误" in text:
            return "debugging"
        if "总结" in text:
            return "summarization"
        return "general"

    def classify_intent(self, task):
        if "写一个API" in task:
            return "generate_service"
        if "代码" in task or "编程" in task:
            return "generate_code"
        if "写" in task or "文章" in task:
            return "writing"
        if "图片" in task or "视觉" in task:
            return "vision"
        if "自动化" in task:
            return "automation"
        return "general"


class Planner:
    def __init__(self, tool_registry=None):
        registry = tool_registry or get_global_registry()
        self.inner = HierarchicalPlanner(tool_registry=registry)
        self.compiler = PlanCompiler()

    def plan(self, context: Dict) -> Dict:
        llm_output = self.inner.plan(context)
        return self.compiler.normalize_output(llm_output)
