"""
Memory Governance — dev-mode permissions, intent validation, mutation trace.

Memory = governed state machine. No silent mutation. No bypass of MemoryLayer.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.contracts.memory_mutation import (
    MemoryMutationIntent,
    MemoryMutationTrace,
    VALID_ACTIONS,
    VALID_OPS,
    VALID_TARGETS,
)
from core.control.runtime_control import RuntimeControl


class MemoryGovernanceError(Exception):
    def __init__(self, message: str, *, code: str = "memory_governance"):
        super().__init__(message)
        self.code = code


class MemoryControl:
    """Control-layer gate for all memory mutations."""

    @classmethod
    def authorize(
        cls,
        control: RuntimeControl,
        raw_intent: Dict[str, Any],
    ) -> MemoryMutationIntent:
        intent = MemoryMutationIntent.from_dict(raw_intent)

        if intent.op not in VALID_OPS:
            raise MemoryGovernanceError(f"Invalid op: {intent.op}")

        if intent.target not in VALID_TARGETS:
            raise MemoryGovernanceError(f"Invalid target: {intent.target}")

        if intent.action not in VALID_ACTIONS:
            raise MemoryGovernanceError(f"Invalid action: {intent.action}")

        if intent.target == "episodic" and intent.action not in ("rollback", "snapshot"):
            raise MemoryGovernanceError(
                "Episodic memory cannot be edited directly; use rollback/snapshot or replay."
            )

        if intent.target == "world_state":
            raise MemoryGovernanceError(
                "world_state must be updated via World Engine + MemoryLayer.save_world_state, not direct mutation."
            )

        if intent.target == "procedural":
            if control.mode != RuntimeControl.DEBUG:
                raise MemoryGovernanceError(
                    "Procedural memory mutation requires debug mode with trace."
                )

        if intent.action in ("delete", "override", "inject", "rollback") and control.is_user_mode():
            raise MemoryGovernanceError(
                "delete/override/inject/rollback require developer or debug mode."
            )

        if intent.inject_test and control.is_user_mode():
            raise MemoryGovernanceError("Test memory injection requires developer mode.")

        if intent.action in ("merge", "override", "inject") and not intent.fact and not intent.record_id:
            if intent.action != "rollback":
                raise MemoryGovernanceError("merge/override/inject require fact or record_id.")

        if intent.action == "rollback" and not intent.snapshot_id:
            raise MemoryGovernanceError("rollback requires snapshot_id.")

        intent.actor = control.mode
        return intent

    @classmethod
    def build_kernel_plan(
        cls,
        intent: MemoryMutationIntent,
        agent_id: str,
        trace_id: str,
    ) -> Dict[str, Any]:
        """Orchestration output → single execute_memory_op syscall."""
        return {
            "task": f"memory:{intent.target}:{intent.action}",
            "task_type": "memory_mutation",
            "intent": "memory_governance",
            "strategy": "memory_control",
            "actions": [
                {
                    "type": "tool",
                    "name": "execute_memory_op",
                    "payload": {
                        "intent": intent.to_dict(),
                        "agent_id": agent_id,
                    },
                }
            ],
            "_meta": {
                "source": "memory_control",
                "mutation": intent.to_dict(),
                "trace_id": trace_id,
                "observable": True,
            },
        }

    @classmethod
    def append_mutation_trace(
        cls,
        agent_id: str,
        trace: MemoryMutationTrace,
        base_dir: str = "./memory_db/agents",
    ) -> None:
        path = Path(base_dir) / agent_id / "mutation_trace.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(trace.to_dict(), ensure_ascii=False)
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    @classmethod
    def list_mutation_traces(
        cls,
        agent_id: str,
        limit: int = 50,
        base_dir: str = "./memory_db/agents",
    ) -> List[Dict[str, Any]]:
        path = Path(base_dir) / agent_id / "mutation_trace.jsonl"
        if not path.exists():
            return []
        lines: List[str] = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    lines.append(line.strip())
        out = []
        for line in lines[-limit:]:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return out

    @classmethod
    def remember_intent(cls, fact: str, *, kind: str = "fact", inject_test: bool = False) -> Dict[str, Any]:
        return MemoryMutationIntent(
            op="update_memory",
            target="semantic",
            action="merge",
            fact=fact,
            kind=kind,
            inject_test=inject_test,
        ).to_dict()
