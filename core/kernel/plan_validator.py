# core/kernel/plan_validator.py

REQUIRED_PLAN_SCHEMA = {
    "plan": list,
    "goals": list,
    "tool_calls": list
}

class PlanValidator:

    def validate(self, plan):

        if not isinstance(plan, dict):
            return False

        for key in REQUIRED_PLAN_SCHEMA:
            if key not in plan:
                return False

        if len(plan["plan"]) == 0:
            return False

        if len(plan["goals"]) == 0:
            return False

        return True
