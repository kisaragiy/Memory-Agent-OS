"""
Output Filter — single exit for LLM / tool / execution payloads.

ModelPolicy → AlignmentFlags → OutputFilter (no scattered cropping).
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional, Union

from core.control.alignment_spec import AlignmentFlags

JsonLike = Union[Dict[str, Any], List[Any], str, int, float, bool, None]

_TRACE_KEYS = frozenset(
    {
        "trace",
        "traces",
        "trace_history",
        "execution_trace",
        "span",
        "spans",
    }
)
_REASONING_KEYS = frozenset(
    {
        "reasoning",
        "chain_of_thought",
        "cot",
        "thought",
        "thoughts",
        "analysis",
        "rationale",
    }
)
_MEMORY_KEYS = frozenset(
    {
        "memory",
        "memory_diff",
        "memory_context",
        "memory_snapshot",
        "mutation",
        "mutations",
        "records",
        "episodes",
        "export_snapshot",
    }
)
_TOOL_IO_KEYS = frozenset(
    {
        "tool_calls",
        "tool_io",
        "tool_input",
        "tool_output",
        "syscall",
        "syscalls",
        "steps",
        "execution_results",
        "payload",
        "stderr",
        "locals",
    }
)
_SYSTEM_META_KEYS = frozenset(
    {
        "_meta",
        "model_policy",
        "execution_gate",
        "alignment_flags",
        "intent_classification",
        "plan_meta",
        "routing",
        "observable",
        "channel",
        "syscall_type",
    }
)
_PLAN_KEYS = frozenset({"plan", "action_plan", "reflection", "observation", "world"})
_GUARD_KEYS = frozenset(
    {
        "guard_decision",
        "guarded_execution",
        "sandbox_journal",
    }
)


class OutputFilter:
    @staticmethod
    def filter_output(
        data: JsonLike,
        flags: AlignmentFlags,
        *,
        depth: int = 0,
        max_depth: int = 8,
    ) -> JsonLike:
        """Crop dict/list payloads according to alignment flags."""
        if depth > max_depth:
            return data
        if isinstance(data, list):
            return [
                OutputFilter.filter_output(item, flags, depth=depth + 1, max_depth=max_depth)
                for item in data
            ]
        if not isinstance(data, dict):
            return data

        out = copy.deepcopy(data)

        if not flags.show_trace:
            OutputFilter._pop_keys(out, _TRACE_KEYS)
            if not flags.show_system_meta:
                out.pop("trace_id", None)

        if not flags.show_reasoning:
            OutputFilter._pop_keys(out, _REASONING_KEYS)

        if not flags.show_memory:
            OutputFilter._pop_keys(out, _MEMORY_KEYS)

        if not flags.show_tool_io:
            OutputFilter._pop_keys(out, _TOOL_IO_KEYS)
            if isinstance(out.get("result"), dict):
                inner = out["result"]
                for key in ("locals", "stderr", "_renderer_meta"):
                    inner.pop(key, None)

        if not flags.show_system_meta:
            OutputFilter._pop_keys(out, _SYSTEM_META_KEYS)
            OutputFilter._pop_keys(out, _PLAN_KEYS)
            OutputFilter._pop_keys(out, _GUARD_KEYS)

        for key, value in list(out.items()):
            if isinstance(value, (dict, list)):
                out[key] = OutputFilter.filter_output(
                    value, flags, depth=depth + 1, max_depth=max_depth
                )
        return out

    @staticmethod
    def filter_renderer_meta(meta: Dict[str, Any], flags: AlignmentFlags) -> Dict[str, Any]:
        filtered = OutputFilter.filter_output(meta, flags)
        return filtered if isinstance(filtered, dict) else {}

    @staticmethod
    def filter_execution_step(step: Dict[str, Any], flags: AlignmentFlags) -> Dict[str, Any]:
        filtered = OutputFilter.filter_output(step, flags)
        return filtered if isinstance(filtered, dict) else step

    @staticmethod
    def filter_http_response(
        payload: Dict[str, Any],
        flags: AlignmentFlags,
        *,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        out = OutputFilter.filter_output(payload, flags)
        if not isinstance(out, dict):
            return {"display": str(out)}
        if flags.show_trace and trace_id:
            out.setdefault("trace_id", trace_id)
        return out

    @staticmethod
    def _pop_keys(target: Dict[str, Any], keys: frozenset) -> None:
        for key in keys:
            target.pop(key, None)
