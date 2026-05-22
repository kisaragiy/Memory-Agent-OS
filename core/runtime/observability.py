from typing import Dict, List
from .event_logger import EventLogger
from .execution_tracer import ExecutionTracer
from .system_metrics import SystemMetrics

class ObservabilityHub:
    def __init__(self):
        self.logger = EventLogger()
        self.tracer = ExecutionTracer()
        self.metrics = SystemMetrics()
        self.traces = {}  # Store traces by session ID
        
    def append_trace(self, session_id: str, step: str, data: Dict):
        """Append a new trace step to the session's trace history"""
        if session_id not in self.traces:
            self.traces[session_id] = []
            
        self.traces[session_id].append({
            "step": step,
            "timestamp": self.metrics.get_current_time(),
            "data": data
        })
        
    def get_trace(self, session_id: str) -> List[Dict]:
        """Retrieve the complete trace for a session"""
        return self.traces.get(session_id, [])
    
    def export_graph(self, session_id: str) -> Dict:
        """Export execution graph for a session"""
        trace = self.get_trace(session_id)
        # In a real implementation, this would generate a graph from the trace
        return {
            "nodes": [{"id": f"step_{i}", "name": step["step"]} for i, step in enumerate(trace)],
            "edges": [{"from": f"step_{i}", "to": f"step_{i+1}"} for i in range(len(trace)-1)]
        }
    
    def log_judgment(self, judgment: Dict):
        """Log a judgment result"""
        self.logger.log("judgment", judgment)

    def filter_output(self, output: Dict, mode: str) -> Dict:
        from core.control.model_policy import ModelPolicy
        from core.control.output_filter import OutputFilter

        flags = ModelPolicy.resolve_flags(mode)
        filtered = OutputFilter.filter_output(output, flags)
        return filtered if isinstance(filtered, dict) else output

    def debug(self, message: str):
        """Log a debug message"""
        self.logger.log("debug", message)

    def trace(self, session_id: str, step: str, data: Dict):
        """Append a trace entry for debugging purposes"""
        self.append_trace(session_id, step, data)

    def user_output(self, output: Dict) -> Dict:
        """Format output for the user mode"""
        return self.filter_output(output, "user")

    def format_output(self, mode, data):
        if mode == 'user':
            return {
                "result": data.get("result")
            }
        elif mode == 'developer':
            return {
                "trace_id": data.get("trace_id"),
                "syscall": data.get("syscall"),
                "tool_route": data.get("tool_route"),
                "execution_result": data.get("execution_result")
            }

    def render(self, mode: str, execution_result: Dict, flags=None):
        from core.control.model_policy import ModelPolicy
        from core.control.output_filter import OutputFilter
        from core.control.presentation_policy import PresentationPolicy

        flags = flags or ModelPolicy.resolve_flags(mode)
        if mode in ("developer", "debug"):
            return OutputFilter.filter_output(execution_result, flags)

        if execution_result.get("status") != "success":
            return execution_result.get("error") or "任务执行失败，请稍后重试。"

        return PresentationPolicy.extract_display_text(
            {"result": execution_result.get("result")}
        )


_hub = ObservabilityHub()


def render(mode: str, execution_result: Dict, flags=None):
    return _hub.render(mode, execution_result, flags)
