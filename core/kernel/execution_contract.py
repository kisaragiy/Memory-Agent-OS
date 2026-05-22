# core/kernel/execution_contract.py

from dataclasses import dataclass, field
import uuid
from core.kernel.goal_hierarchy import Goal
from core.kernel.tool_router import ToolRouter

@dataclass
class ExecutionContract:
    input_text: str
    plan: dict
    goals: list[Goal]
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def validate_goal(self, goal):
        if not isinstance(goal, Goal):
            raise ValueError("Invalid goal type")
        if goal.type == "execution" and not goal.immutable:
            raise ValueError("Execution goals must be immutable")

    def validate_tool_call(self, tool_name):
        if not ToolRouter.exists(tool_name):
            raise ValueError(f"Tool {tool_name} is not registered")

    def enforce_execution_path(self):
        # Placeholder for enforcing execution path
        pass

    def block_unauthorized_state_mutation(self):
        # Placeholder for blocking unauthorized state mutation
        pass
