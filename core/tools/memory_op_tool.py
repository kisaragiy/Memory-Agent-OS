"""
execute_memory_op — sole kernel syscall for governed memory writes.
"""

from __future__ import annotations

from typing import Any, Dict

from core.contracts.memory_mutation import MemoryMutationIntent
from core.memory import get_memory_layer


class MemoryOpTool:
    """Invoked only via ExecutionEngine (never call MemoryLayer from UI/API)."""

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            return {
                "status": "error",
                "result": None,
                "error": "payload must be object",
            }
        agent_id = payload.get("agent_id") or "local-agent"
        raw = payload.get("intent") or payload
        trace_id = payload.get("trace_id", "")

        try:
            intent = MemoryMutationIntent.from_dict(raw)
            layer = get_memory_layer()
            result = layer.apply_mutation(agent_id, intent, trace_id=trace_id)
            return {
                "status": "success",
                "result": result,
                "error": None,
                "_meta": {
                    "source": "execute_memory_op",
                    "mutation": intent.to_dict(),
                    "observable": True,
                },
            }
        except Exception as exc:
            return {
                "status": "error",
                "result": None,
                "error": str(exc),
                "_meta": {"source": "execute_memory_op", "observable": True},
            }
