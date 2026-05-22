"""Intent router / execution isolation smoke tests."""

from core.control.intent_router import IntentRouter
from core.contracts.intent import ExecutionChannel, IntentType
from core.orchestration.orchestrator import KernelOrchestrator


def test_greeting_is_chat_narrative():
    c = IntentRouter.classify("你好", {})
    assert c.route.intent == IntentType.CHAT
    assert c.route.allow_execute_code is False


def test_story_is_narrative_not_code():
    c = IntentRouter.classify("写一段恐怖故事短篇", {})
    assert c.route.intent == IntentType.NARRATIVE
    assert c.route.allow_execute_code is False
    assert not IntentRouter.looks_like_natural_language("print(1)")


def test_natural_language_not_executable():
    assert IntentRouter.looks_like_natural_language("你好")
    assert IntentRouter.looks_like_natural_language("写一段恐怖故事短篇")
    assert not IntentRouter.is_safe_python_snippet("你好")


def test_plan_no_execute_code_for_greeting():
    o = KernelOrchestrator()
    clf = IntentRouter.classify("你好", {})
    plan = o.build_plan({"input": "你好", "agent_id": "t"}, clf)
    names = [a.get("name") for a in plan.get("actions", [])]
    assert names == ["narrative_respond"]


def test_plan_story_narrative():
    o = KernelOrchestrator()
    clf = IntentRouter.classify("写一段恐怖故事短篇", {})
    plan = o.build_plan({"input": "写一段恐怖故事短篇", "agent_id": "t"}, clf)
    names = [a.get("name") for a in plan.get("actions", [])]
    assert "execute_code" not in names
    assert "narrative_respond" in names


def test_code_snippet_allowed():
    c = IntentRouter.classify('print("hi")', {})
    assert c.route.intent == IntentType.CODE
    assert c.route.allow_execute_code is True
