from datetime import datetime as now

class CheckpointManager:
    def __init__(self):
        self.checkpoints = []

    def save(self, state):
        self.checkpoints.append({
            "state": state.copy(),
            "timestamp": now()
        })

class FailureDetector:
    def detect(self, result, context):
        if result is None:
            return True
        if "error" in result:
            return True
        if context.get("execution_time") > 10:
            return True
        return False

class RollbackEngine:
    def rollback(self, kernel):
        if not kernel.checkpoints:
            return {"status": "no_checkpoint"}
        last_state = kernel.checkpoints[-1]
        kernel.restore(last_state["state"])
        return {"status": "rolled_back"}

class RetryPolicy:
    def should_retry(self, attempt, failure):
        if attempt > 3:
            return False
        if failure.get("type") == "tool_error":
            return True
        return False

class DegradedMode:
    def activate(self, kernel):
        kernel.tool_registry.disable_high_risk_tools()
        kernel.planner.switch_to_simple_mode()
        kernel.reflective_loop.reduce_depth()
        return "degraded_mode_on"

class FailureRecoveryKernel:
    def __init__(self):
        self.checkpoint_manager = CheckpointManager()
        self.detector = FailureDetector()
        self.rollback_engine = RollbackEngine()
        self.retry_policy = RetryPolicy()
        self.degraded_mode = DegradedMode()

    def safe_execute(self, kernel, execution_fn, context):
        self.checkpoint_manager.save(kernel.state)
        attempt = 0
        while True:
            result = execution_fn(context)
            if not self.detector.detect(result, context):
                return result
            # === failure path ===
            attempt += 1
            if self.retry_policy.should_retry(attempt, result):
                continue
            # rollback first
            self.rollback_engine.rollback(kernel)
            # degrade system if repeated failure
            if attempt >= 2:
                self.degraded_mode.activate(kernel)
                return {
                    "result": None,
                    "mode": "degraded",
                    "reason": "recovery_triggered"
                }
            break

    def handle_failure(self, error):
        self.obs.logger.log("failure", {
            "error": error,
            "severity": "high"
        })
        self.obs.tracer.record("failure_point", error)
