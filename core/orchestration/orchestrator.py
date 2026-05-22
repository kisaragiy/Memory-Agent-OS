"""
Kernel Orchestrator — decision system (Brain).

Intent routing → ModelPolicy (capability) → plan → ExecutionEngine (runtime).
"""

from __future__ import annotations

from typing import Dict, List, Optional

from core.control.execution_gate import ExecutionGate
from core.control.intent_router import IntentRouter
from core.control.alignment_spec import AlignmentFlags
from core.control.model_policy import ModelMode, ModelPolicy
from core.contracts.intent import (
    ExecutionChannel,
    IntentClassification,
    IntentRoute,
    IntentType,
)
from core.planner.planner import Planner
from core.protocol.code_sanitizer import sanitize


class KernelOrchestrator:
    """
    Routing table (intent classification):
      execute_code  → 1+2, print(), x=5, verified Python snippets
      llm           → natural language, chat, narrative
      memory        → remember:/记住: (handled in entry before orchestrator)
      guard         → UI action plans
    """

    def __init__(self, tool_registry=None):
        self.planner = Planner(tool_registry=tool_registry)

    @staticmethod
    def is_direct_executable(text: str) -> bool:
        return IntentRouter.is_safe_python_snippet(text)

    def build_plan(
        self,
        context: Dict,
        classification: Optional[IntentClassification] = None,
    ) -> Dict:
        user_input = (context.get("input") or "").strip()
        agent_id = context.get("agent_id", "local-agent")
        control_mode = context.get("control_mode", "user")
        flags = ModelPolicy.resolve_flags(control_mode)
        context["alignment_flags"] = flags.to_dict()

        if classification is None:
            classification = IntentRouter.classify(user_input, context)
        route = classification.route
        routing = ModelPolicy.route_target(route)

        if not flags.enable_code_execution and routing == "execute_code":
            routing = "llm"
        if not flags.enable_narrative and routing == "llm":
            routing = "blocked"

        model_mode = ModelPolicy.resolve_mode(control_mode, route.intent)
        context["model_mode"] = model_mode.value
        context["routing"] = routing

        if routing == "blocked":
            plan = self._blocked_plan(user_input, flags)
        elif routing == "llm":
            plan = self._llm_plan(
                user_input, agent_id, context, route, model_mode
            )
        elif routing == "execute_code":
            plan = self._code_plan(user_input, agent_id, context, route, model_mode)
        else:
            plan = self._llm_plan(
                user_input, agent_id, context, route, model_mode
            )

        plan.setdefault("_meta", {})["routing"] = routing
        plan["_meta"]["model_mode"] = model_mode.value
        plan["_meta"]["model_policy"] = ModelPolicy.get_policy(model_mode)
        plan["_meta"]["alignment_flags"] = flags.to_dict()
        plan["_meta"]["intent_trace"] = {
            "intent": route.intent.value,
            "route": routing,
            "mode": control_mode,
            "policy": model_mode.value,
        }
        return ExecutionGate.enforce_plan(plan, route, flags)

    @staticmethod
    def _blocked_plan(user_input: str, flags: AlignmentFlags) -> Dict:
        actions: List[Dict] = []
        if flags.enable_narrative:
            actions.append(
                {
                    "type": "tool",
                    "name": "narrative_respond",
                    "payload": {
                        "prompt": "当前模式不允许该类型的生成，请切换开发者模式或调整对齐设置。",
                    },
                }
            )
        return {
            "task": user_input,
            "task_type": "blocked",
            "intent": IntentType.UNKNOWN.value,
            "strategy": "alignment_blocked",
            "actions": actions,
            "_meta": {
                "routing": "blocked",
                "alignment_flags": flags.to_dict(),
                "blocked_reason": "capability_disabled",
            },
        }

    def _code_plan(
        self,
        user_input: str,
        agent_id: str,
        context: Dict,
        route: IntentRoute,
        model_mode: ModelMode,
    ) -> Dict:
        if IntentRouter.is_safe_python_snippet(user_input):
            return {
                "task": user_input,
                "task_type": "direct_code",
                "intent": IntentType.CODE.value,
                "strategy": "verified_snippet",
                "actions": [
                    {
                        "type": "tool",
                        "name": "execute_code",
                        "payload": {"code": user_input},
                    }
                ],
                "_meta": {
                    "source": "direct_verified",
                    "intent": route.intent.value,
                    "routing": "execute_code",
                },
            }
        return self._plan_with_planner(context, route, model_mode)

    def _llm_plan(
        self,
        user_input: str,
        agent_id: str,
        context: Dict,
        route: IntentRoute,
        model_mode: ModelMode,
    ) -> Dict:
        task_type = "chat" if route.intent == IntentType.CHAT else "narrative"
        return {
            "task": user_input,
            "task_type": task_type,
            "intent": route.intent.value,
            "strategy": "model_policy_llm",
            "actions": [
                {
                    "type": "tool",
                    "name": "narrative_respond",
                    "payload": {
                        "prompt": user_input,
                        "agent_id": agent_id,
                        "memory_context": context,
                        "control_mode": context.get("control_mode", "user"),
                        "model_mode": model_mode.value,
                        "intent": route.intent.value,
                    },
                }
            ],
            "_meta": {
                "source": "intent_router",
                "intent": route.intent.value,
                "channel": route.channel.value,
                "routing": "llm",
                "observable": True,
            },
        }

    def _plan_with_planner(
        self, context: Dict, route: IntentRoute, model_mode: ModelMode
    ) -> Dict:
        user_input = context.get("input", "")
        agent_id = context.get("agent_id", "local-agent")
        context["task_type"] = context.get("task_type") or "code_generation"
        try:
            plan = self.planner.plan(context)
            if not plan.get("actions"):
                raise ValueError("Planner returned empty actions")
            plan.setdefault("_meta", {})["source"] = "planner"
            plan["_meta"]["intent"] = route.intent.value
            plan["_meta"]["routing"] = "execute_code"
            return plan
        except Exception as exc:
            plan = self._llm_plan(
                user_input,
                agent_id,
                context,
                route,
                model_mode,
            )
            plan["_meta"]["fallback_reason"] = str(exc)
            plan["_meta"]["routing"] = "llm"
            return plan

    def plan_to_syscalls(
        self,
        plan: Dict,
        trace_id: str,
        route: Optional[IntentRoute] = None,
    ) -> List[Dict]:
        if route is None:
            meta = plan.get("_meta") or {}
            intent_str = meta.get("intent", IntentType.NARRATIVE.value)
            try:
                intent = IntentType(intent_str)
            except ValueError:
                intent = IntentType.NARRATIVE
            route = IntentRoute(
                intent=intent,
                channel=ExecutionChannel.NARRATIVE,
                allow_execute_code=(intent == IntentType.CODE),
            )

        syscalls: List[Dict] = []
        for index, action in enumerate(plan.get("actions") or []):
            if action.get("type") != "tool":
                continue
            name = action.get("name")
            if not name:
                continue
            payload = dict(action.get("payload") or {})
            if name == "execute_code":
                payload["code"] = self._normalize_code(
                    self._extract_code(payload, plan)
                )
            if name == "execute_memory_op":
                payload.setdefault("agent_id", plan.get("agent_id"))
            syscalls.append(
                {
                    "type": name,
                    "payload": payload,
                    "trace_id": f"{trace_id}:{index}",
                }
            )

        flags = AlignmentFlags.from_dict((plan.get("_meta") or {}).get("alignment_flags"))
        return ExecutionGate.filter_syscalls(syscalls, route, flags)

    @staticmethod
    def _extract_code(payload: Dict, plan: Dict) -> str:
        if payload.get("code"):
            return str(payload["code"])
        return str(plan.get("task") or "")

    @staticmethod
    def _normalize_code(code: str) -> str:
        code = (code or "").strip()
        if not code:
            return "pass"
        if IntentRouter.is_safe_python_snippet(code):
            return code
        if IntentRouter.looks_like_natural_language(code):
            raise ValueError("natural_language_blocked_from_execution")
        return sanitize(code)
