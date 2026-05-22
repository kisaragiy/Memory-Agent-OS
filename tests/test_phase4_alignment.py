"""Phase 4 paths respect AlignmentFlags + OutputFilter."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.control.model_policy import ModelPolicy
from core.control.output_filter import OutputFilter
from core.control.runtime_control import RuntimeControl
from core.contracts.action_plan import ActionIntent, ActionPlan
from core.perception.action_plan_presenter import ActionPlanPresenter


def test_phase4b_user_payload_filtered():
    flags = ModelPolicy.resolve_flags(RuntimeControl.USER)
    plan = ActionPlan(
        intents=[
            ActionIntent(
                intent_id="i1",
                action_type="click",
                target_label="提交",
                risk_level="low",
            )
        ]
    )
    dev = ActionPlanPresenter.render_developer(plan)
    payload = {
        "result": dev["summary"],
        "trace_id": "t-phase4",
        "plan": {"task": "click"},
        "action_plan": dev["action_plan"],
        "steps": [{"status": "success", "tool_calls": []}],
        "observation": {"elements": []},
    }
    out = OutputFilter.filter_output(payload, flags)
    assert "action_plan" not in out
    assert "steps" not in out
    assert "observation" not in out
    assert out.get("result")


def test_phase4_guard_journal_hidden_for_user():
    flags = ModelPolicy.resolve_flags(RuntimeControl.USER)
    payload = {
        "result": "done",
        "sandbox_journal": [{"action": "click"}],
        "guard_decision": {"approved": True},
        "guarded_execution": {"receipts": []},
    }
    out = OutputFilter.filter_output(payload, flags)
    assert "sandbox_journal" not in out
    assert "guard_decision" not in out
