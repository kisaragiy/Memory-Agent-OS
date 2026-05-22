from .llm_judge_v2 import Judgment
from core.runtime.event_logger import EventLogger
from core.runtime.execution_tracer import ExecutionTracer
from core.runtime.system_metrics import SystemMetrics

class ObservabilityHub:
    def __init__(self):
        self.logger = EventLogger()
        self.tracer = ExecutionTracer()
        self.metrics = SystemMetrics()

    def log_judgment(self, judgment: Judgment):
        self.logger.log("judgment", {
            "accuracy": judgment.accuracy,
            "reasoning": judgment.reasoning_quality,
            "efficiency": judgment.efficiency,
            "safety": judgment.safety
        })
