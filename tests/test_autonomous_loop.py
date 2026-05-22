"""Phase 5 — AutonomousOSLoop (no live desktop required)."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.orchestration.autonomous_loop import AutonomousOSLoop
from core.perception.gate import ActionPlanGate


class _FakeRuntime:
    agent_id = "test-agent"
    control_mode = "developer"

    class control:
        mode = "developer"

    def __init__(self):
        self.calls = 0

    def entry(self, text, user_confirmed=False):
        self.calls += 1
        return f"done step {self.calls}: {text[:30]}"

    def _alignment_flags(self):
        from core.control.model_policy import ModelPolicy

        return ModelPolicy.resolve_flags("developer")


def test_autonomous_stops_on_simple_nl():
    loop = AutonomousOSLoop(max_steps=3)
    rt = _FakeRuntime()
    result = loop.run(rt, "你好")
    assert result.status == "success"
    assert len(result.steps) == 1
    assert rt.calls == 1


def test_autonomous_ui_goal_may_continue():
    goal = "点击开始按钮"
    assert ActionPlanGate.should_plan(goal)
    loop = AutonomousOSLoop(max_steps=2)
    rt = _FakeRuntime()
    result = loop.run(rt, goal, user_confirmed=True)
    assert result.status in ("success", "max_steps", "incomplete")
    assert rt.calls >= 1
