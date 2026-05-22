class KernelState:

    def __init__(self):

        self.execution_pipeline = [
            "perception",
            "planning",
            "execution",
            "reflection"
        ]

        self.stability_score = 1.0
        self.allowed_mutation_depth = 1

def detect_kernel_drift(old, new):

    drift = 0

    # pipeline变化
    if old.execution_pipeline != new.execution_pipeline:

        drift += len(
            set(old.execution_pipeline)
            - set(new.execution_pipeline)
        ) * 0.5

    # identity变化
    if old.identity != new.identity:
        drift += 0.4

    return min(drift, 1.0)

class KernelStabilizer:

    def __init__(self):
        self.allowed_mutation_depth = 1

    def validate(self, old_kernel, new_kernel):

        drift = detect_kernel_drift(old_kernel, new_kernel)

        # ❌ 禁止结构级崩坏
        if drift > 0.6:
            return False

        # ⚠️ 限制中等变化
        if drift > 0.3:
            new_kernel.execution_pipeline = old_kernel.execution_pipeline

        return True

    def enforce_mutation_limit(self, change_plan):
        if change_plan.depth > self.allowed_mutation_depth:
            return "reject"
        if "execution_pipeline" in change_plan.modified_fields:
            return "reject"
        return "allow"
