"""ModelPolicy — routing, modes, invocation specs."""

from core.control.model_policy import ModelMode, ModelPolicy
from core.contracts.intent import ExecutionChannel, IntentRoute, IntentType


def test_route_target_code():
    route = IntentRoute(
        intent=IntentType.CODE,
        channel=ExecutionChannel.PLANNER,
        allow_execute_code=True,
    )
    assert ModelPolicy.route_target(route) == "execute_code"


def test_route_target_llm():
    route = IntentRoute(
        intent=IntentType.CHAT,
        channel=ExecutionChannel.NARRATIVE,
        allow_execute_code=False,
    )
    assert ModelPolicy.route_target(route) == "llm"


def test_resolve_mode_user_chat():
    mode = ModelPolicy.resolve_mode("user", IntentType.CHAT)
    assert mode == ModelMode.CREATIVE


def test_resolve_mode_strict_code():
    mode = ModelPolicy.resolve_mode(
        "user", IntentType.CODE, task_type="code_generation"
    )
    assert mode == ModelMode.STRICT


def test_build_narrative_invocation_has_system():
    spec = ModelPolicy.build_narrative_invocation(
        {
            "prompt": "你好",
            "scaffold": "",
            "memory_prompt": "",
            "control_mode": "user",
            "intent": "chat",
        }
    )
    assert spec.system
    assert "你好" in spec.user
    assert spec.max_tokens <= 800


def test_build_planner_invocation_strip_fences():
    spec = ModelPolicy.build_planner_invocation(
        {"input": "print(1)", "control_mode": "user", "task_type": "code"}
    )
    assert spec.strip_fences is True
    assert "Python" in spec.system or "python" in spec.system.lower()
