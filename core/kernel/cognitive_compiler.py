class CognitiveProgram:
    def __init__(self):
        self.pipeline = [
            "perception",
            "planning",
            "execution",
            "reflection"
        ]
        self.optimizations = []

class CognitiveCompiler:
    def __init__(self, kernel_stabilizer):
        self.kernel_stabilizer = kernel_stabilizer

    def compile(self, program, feedback, kernel_state):
        proposed = self.generate_new_program(program, feedback)

        # === kernel guard ===
        if not self.kernel_stabilizer.validate(kernel_state, proposed):
            return program  # rollback

        return proposed

    def generate_new_program(self, program, feedback):
        optimized = CognitiveProgram()
        for stage in program.pipeline:
            optimized.pipeline.append(self.optimize_stage(stage, feedback))
        return optimized

    def optimize_stage(self, stage, feedback):
        if stage == "planning" and feedback["planning_error"] > 0.5:
            return "hierarchical_planning_v2"
        if stage == "reflection" and feedback["reflection_quality"] < 0.4:
            return "meta_reflection_enhanced"
        return stage

    def should_recompile(self, metrics):
        return (
            metrics["performance_drop"] > 0.3 or
            metrics["reflection_instability"] > 0.4
        )

    def validate_compilation(self, old_program, new_program):
        if len(set(old_program.pipeline) - set(new_program.pipeline)) > 1:
            return False
        return True
