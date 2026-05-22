"""Per-trace span collection (complements ObservabilityHub.traces)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.runtime.system_metrics import SystemMetrics


class ExecutionTracer:
    def __init__(self):
        self._metrics = SystemMetrics()
        self._spans: Dict[str, List[Dict[str, Any]]] = {}

    def start_span(self, trace_id: str, name: str, meta: Optional[Dict] = None) -> None:
        self._spans.setdefault(trace_id, []).append(
            {
                "span": name,
                "event": "start",
                "timestamp": self._metrics.get_current_time(),
                "meta": meta or {},
            }
        )

    def end_span(self, trace_id: str, name: str, meta: Optional[Dict] = None) -> None:
        self._spans.setdefault(trace_id, []).append(
            {
                "span": name,
                "event": "end",
                "timestamp": self._metrics.get_current_time(),
                "meta": meta or {},
            }
        )

    def get_spans(self, trace_id: str) -> List[Dict[str, Any]]:
        return list(self._spans.get(trace_id, []))
