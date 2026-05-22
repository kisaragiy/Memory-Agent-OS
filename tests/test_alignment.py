"""Alignment flags + output filter."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.control.alignment_spec import AlignmentFlags
from core.control.model_policy import ModelPolicy
from core.control.output_filter import OutputFilter
from core.control.runtime_control import RuntimeControl


def test_resolve_flags_user_hides_internals():
    flags = ModelPolicy.resolve_flags(RuntimeControl.USER)
    assert flags.show_trace is False
    assert flags.show_tool_io is False
    assert flags.enable_code_execution is True


def test_resolve_flags_debug_autonomy():
    flags = ModelPolicy.resolve_flags(RuntimeControl.DEBUG)
    assert flags.show_trace is True
    assert flags.enable_autonomy is True


def test_filter_output_strips_trace():
    flags = ModelPolicy.resolve_flags(RuntimeControl.USER)
    data = {
        "result": "ok",
        "trace": [{"step": "a"}],
        "trace_id": "t-1",
        "reasoning": "hidden",
        "memory": {"facts": []},
        "tool_calls": [{"name": "execute_code"}],
        "plan": {"actions": []},
        "_meta": {"routing": "llm"},
    }
    out = OutputFilter.filter_output(data, flags)
    assert out["result"] == "ok"
    assert "trace" not in out
    assert "reasoning" not in out
    assert "memory" not in out
    assert "tool_calls" not in out
    assert "plan" not in out
    assert "_meta" not in out
    assert "trace_id" not in out


def test_filter_output_developer_keeps_trace():
    flags = ModelPolicy.resolve_flags(RuntimeControl.DEVELOPER)
    data = {"result": "ok", "trace": [{"step": "a"}], "trace_id": "t-1"}
    out = OutputFilter.filter_output(data, flags)
    assert out.get("trace")
    assert out.get("trace_id") == "t-1"


def test_alignment_flags_merge():
    base = ModelPolicy.resolve_flags(RuntimeControl.USER)
    merged = base.merge(show_trace=True)
    assert merged.show_trace is True
    assert merged.show_memory is False


def _run_all() -> int:
    tests = [
        test_resolve_flags_user_hides_internals,
        test_resolve_flags_debug_autonomy,
        test_filter_output_strips_trace,
        test_filter_output_developer_keeps_trace,
        test_alignment_flags_merge,
    ]
    failed = 0
    for fn in tests:
        try:
            fn()
            print(f"OK  {fn.__name__}")
        except Exception as exc:
            failed += 1
            print(f"FAIL {fn.__name__}: {exc}")
    return failed


if __name__ == "__main__":
    try:
        import pytest
    except ImportError:
        raise SystemExit(_run_all())
    raise SystemExit(pytest.main([__file__, "-v"]))
