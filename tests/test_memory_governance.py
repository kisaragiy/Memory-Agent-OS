"""Memory governance — kernel path only."""

import pytest

from core.control.memory_control import MemoryControl, MemoryGovernanceError
from core.control.runtime_control import RuntimeControl


def test_user_cannot_delete():
    ctrl = RuntimeControl(mode=RuntimeControl.USER)
    with pytest.raises(MemoryGovernanceError):
        MemoryControl.authorize(
            ctrl,
            {
                "op": "update_memory",
                "target": "semantic",
                "action": "delete",
                "record_id": "x",
            },
        )


def test_episodic_direct_edit_blocked():
    ctrl = RuntimeControl(mode=RuntimeControl.DEVELOPER)
    with pytest.raises(MemoryGovernanceError):
        MemoryControl.authorize(
            ctrl,
            {
                "op": "update_memory",
                "target": "episodic",
                "action": "merge",
                "fact": "hack",
            },
        )


def test_world_state_blocked():
    ctrl = RuntimeControl(mode=RuntimeControl.DEBUG)
    with pytest.raises(MemoryGovernanceError):
        MemoryControl.authorize(
            ctrl,
            {
                "op": "update_memory",
                "target": "world_state",
                "action": "merge",
                "fact": "x",
            },
        )


def test_build_kernel_plan_uses_execute_memory_op():
    intent = MemoryControl.authorize(
        RuntimeControl(mode=RuntimeControl.DEVELOPER),
        MemoryControl.remember_intent("test fact"),
    )
    plan = MemoryControl.build_kernel_plan(intent, "agent-1", "trace-1")
    assert plan["actions"][0]["name"] == "execute_memory_op"
