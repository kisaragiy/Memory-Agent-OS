# core/kernel/execution_scheduler.py

from fastapi import HTTPException
import uuid

class ExecutionContract:
    def __init__(self, input_text: str, plan: dict):
        self.input = input_text
        self.plan = plan
        self.execution_mode = "deterministic"
        self.trace_id = str(uuid.uuid4())

class ExecutionScheduler:

    def __init__(self, tool_router):
        self.tool_router = tool_router

    def validate_contract(self, contract: ExecutionContract):
        if not isinstance(contract, ExecutionContract):
            raise HTTPException(status_code=400, detail="Invalid contract type")
        if "steps" not in contract.plan or "tools" not in contract.plan:
            raise HTTPException(status_code=400, detail="Incomplete plan")

    def enforce_determinism(self, plan: dict):
        # Ensure that the plan is deterministic
        if plan.get("execution_mode", "") != "deterministic":
            raise HTTPException(status_code=400, detail="Non-deterministic execution mode")

    def execute_steps_sequentially(self, contract: ExecutionContract):
        for step in contract.plan["steps"]:
            tool_name = step.get("tool")
            if not tool_name:
                raise HTTPException(status_code=400, detail="Tool name missing in step")
            self.tool_router.dispatch(tool_name)

    def forbid_direct_tool_call(self):
        # This method is a placeholder to enforce the rule that tools cannot be called directly
        pass
