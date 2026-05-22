from core.kernel.hardening import SystemHardeningProfile, AuditLogger

class CognitiveOSKernel:
    def __init__(self, planner, memory, reflection, compiler, identity, tool_registry):
        self.modules = {
            "planner": planner,
            "memory": memory,
            "reflection": reflection,
            "compiler": compiler,
            "identity": identity
        }
        self.state = "stable"
        self.tool_registry = tool_registry
        self.hardening = SystemHardeningProfile()
        self.audit = AuditLogger()

    def boot_hardened_mode(self):
        self.hardening.enforce_least_privilege(self.tool_registry)
        self.hardening.enforce_isolation(self)
        self.hardening.lock_self_modification(self)

    def enforce_policy(self, plan):
        if "execute" in plan:
            plan["execute"] = None
        plan["tool_calls"] = self.convert_to_sandbox(plan)
        return plan

    def convert_to_sandbox(self, plan):
        tool_calls = []
        for action in plan.get("actions", []):
            if "tool" in action:
                tool_calls.append({
                    "tool": action["tool"],
                    "payload": action.get("payload", {})
                })
        return tool_calls

    def attach_observability(self, obs):
        self.obs = obs

    def execute_stage(self, stage, context):
        self.obs.logger.log("stage_start", {"stage": stage})
        result = self._execute(stage, context)
        self.obs.logger.log("stage_end", {
            "stage": stage,
            "result": result
        })
        self.obs.tracer.record(stage, result)
        return result
