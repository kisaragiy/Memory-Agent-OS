from typing import Dict, List
import json
from core.protocol.task_types import TASK_TYPES
from core.protocol.code_sanitizer import sanitize

class PlanCompiler:
    def __init__(self):
        pass

    def compile(self, raw_output: str) -> Dict:
        # Placeholder for parsing and structuring logic
        plan = {
            "task": "",
            "strategy": "",
            "task_type": "",
            "actions": []
        }

        # Example of extracting intent and generating actions
        if "API" in raw_output or "接口" in raw_output:
            plan["task"] = raw_output
            plan["strategy"] = "default_strategy"
            plan["task_type"] = "api_design"
            plan["actions"].append({
                "type": "tool",
                "name": "execute_code",
                "payload": {"code": sanitize(self.generate_api_code(raw_output))}
            })
        elif "bug" in raw_output or "错误" in raw_output:
            plan["task"] = raw_output
            plan["strategy"] = "default_strategy"
            plan["task_type"] = "debugging"
            plan["actions"].append({
                "type": "tool",
                "name": "execute_code",
                "payload": {"code": sanitize(self.generate_debug_code(raw_output))}
            })
        else:
            plan["task"] = raw_output
            plan["strategy"] = "default_strategy"
            plan["task_type"] = "general"
            plan["actions"].append({
                "type": "tool",
                "name": "execute_code",
                "payload": {"code": sanitize(f"# Fallback code for {raw_output}")}
            })

        # Validate task_type
        if plan["task_type"] not in TASK_TYPES:
            plan["task_type"] = self._map_to_closest_semantic(plan["task_type"])

        return plan

    def generate_api_code(self, task: str) -> str:
        # Placeholder for code generation logic
        return f"# API design code for {task}"

    def generate_debug_code(self, task: str) -> str:
        # Placeholder for code generation logic
        return f"# Debugging code for {task}"

    def _map_to_closest_semantic(self, task_type):
        # Placeholder for mapping logic
        if "api_design" in task_type:
            return "code_generation"
        elif "debugging" in task_type:
            return "debugging"
        elif "summarization" in task_type:
            return "analysis"
        else:
            return "general"

    def normalize_output(self, raw: str) -> Dict:
        if isinstance(raw, dict):
            plan = raw
        else:
            try:
                parsed = json.loads(raw)
                if not isinstance(parsed, dict):
                    raise ValueError("Plan JSON must be an object")
                plan = parsed
            except (json.JSONDecodeError, TypeError) as e:
                raise ValueError(f"Invalid planner output: {e}") from e

        for action in plan.get("actions") or []:
            payload = action.get("payload") or {}
            if "code" not in payload and payload.get("prompt"):
                payload["code"] = payload.pop("prompt")
            action["payload"] = payload

        if plan.get("task_type") and plan["task_type"] not in TASK_TYPES:
            plan["task_type"] = self._map_to_closest_semantic(plan["task_type"])

        return plan
