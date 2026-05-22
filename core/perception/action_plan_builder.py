"""
Phase 4B — Build UI action intents from observation (no execution, no I/O).
"""

from __future__ import annotations

import re
from typing import List, Optional

from core.contracts.action_plan import ActionIntent, ActionPlan
from core.contracts.perception import ObservationState, UIElement


class ActionPlanBuilder:
    """Synthesizes ActionPlan from observation + user goal. Not a kernel planner."""

    @staticmethod
    def build(
        user_goal: str,
        observation: Optional[ObservationState],
    ) -> ActionPlan:
        meta = {"source": "action_plan_builder", "phase": "4B"}
        constraints = [
            "plan_only",
            "execution_allowed=false",
            "requires Phase 4C confirmation",
        ]

        if observation is None or not observation.captured:
            meta["source"] = "action_plan_fallback"
            meta["fallback_reason"] = "no_observation"
            meta["observable"] = True
            return ActionPlan(
                user_goal=user_goal,
                intents=[],
                constraints=constraints
                + ["需要先完成屏幕观察（--observe 或 SCREEN_OBSERVATION_HINT）"],
                _meta=meta,
            )

        elements = observation.elements
        if not elements:
            meta["source"] = "action_plan_fallback"
            meta["fallback_reason"] = "empty_ui_elements"
            meta["observable"] = True
            return ActionPlan(
                user_goal=user_goal,
                intents=[],
                constraints=constraints + ["观察结果中无 UI 元素"],
                _meta=meta,
            )

        intents = ActionPlanBuilder._synthesize_intents(user_goal, elements)
        meta["intent_count"] = len(intents)
        meta["observation_source"] = observation.source

        return ActionPlan(
            user_goal=user_goal,
            intents=intents,
            requires_confirmation=True,
            constraints=constraints,
            _meta=meta,
        )

    @staticmethod
    def _synthesize_intents(user_goal: str, elements: List[UIElement]) -> List[ActionIntent]:
        goal = (user_goal or "").strip()
        intents: List[ActionIntent] = []

        click_target = ActionPlanBuilder._extract_click_target(goal)
        type_text = ActionPlanBuilder._extract_type_text(goal)

        if click_target:
            el = ActionPlanBuilder._match_element(click_target, elements)
            if el:
                params = {}
                if el.bounds:
                    params["bounds"] = el.bounds
                intents.append(
                    ActionIntent.create(
                        "click",
                        target_label=el.label,
                        target_element_id=el.element_id,
                        parameters=params,
                        risk_level="medium",
                        rationale=f"用户意图：点击「{click_target}」",
                    )
                )
            else:
                intents.append(
                    ActionIntent.create(
                        "click",
                        target_label=click_target,
                        risk_level="high",
                        rationale=f"未在观察中匹配到元素，目标：{click_target}",
                    )
                )

        if type_text:
            field_el = ActionPlanBuilder._find_input_field(elements)
            params = {"text": type_text}
            if field_el and field_el.bounds:
                params["bounds"] = field_el.bounds
            intents.append(
                ActionIntent.create(
                    "type_text",
                    target_label=field_el.label if field_el else "输入框",
                    target_element_id=field_el.element_id if field_el else "",
                    parameters=params,
                    risk_level="medium",
                    rationale=f"输入文本：{type_text[:50]}",
                )
            )

        if ActionPlanBuilder._wants_open(goal):
            nav = ActionPlanBuilder._match_element(
                ActionPlanBuilder._extract_open_target(goal) or "浏览器", elements
            )
            intents.append(
                ActionIntent.create(
                    "navigate",
                    target_label=nav.label if nav else "应用/页面",
                    target_element_id=nav.element_id if nav else "",
                    risk_level="high",
                    rationale="打开或切换应用/页面",
                )
            )

        if not intents and elements:
            primary = elements[0]
            intents.append(
                ActionIntent.create(
                    "focus",
                    target_label=primary.label,
                    target_element_id=primary.element_id,
                    risk_level="low",
                    rationale="默认聚焦首要 UI 元素",
                )
            )

        return intents

    @staticmethod
    def _match_element(label_hint: str, elements: List[UIElement]) -> Optional[UIElement]:
        hint = label_hint.lower()
        for el in elements:
            if hint in (el.label or "").lower():
                return el
        for el in elements:
            if (el.label or "").lower() in hint:
                return el
        return None

    @staticmethod
    def _find_input_field(elements: List[UIElement]) -> Optional[UIElement]:
        for role in ("textbox", "input", "searchbox", "combobox"):
            for el in elements:
                if el.role == role:
                    return el
        for el in elements:
            if "输入" in (el.label or ""):
                return el
        return None

    @staticmethod
    def _extract_click_target(goal: str) -> Optional[str]:
        for pat in (
            r"点击[「\"']?([^「\"'」]+)[」\"']?",
            r"按[一下]?[「\"']?([^「\"'」]+)[」\"']?",
            r"click\s+[\"']?([^\"']+)[\"']?",
        ):
            m = re.search(pat, goal, re.I)
            if m:
                return m.group(1).strip()
        return None

    @staticmethod
    def _extract_type_text(goal: str) -> Optional[str]:
        for pat in (
            r"输入[「\"']?([^「\"'」]+)[」\"']?",
            r"填写[「\"']?([^「\"'」]+)[」\"']?",
            r"type\s+[\"']?([^\"']+)[\"']?",
        ):
            m = re.search(pat, goal, re.I)
            if m:
                return m.group(1).strip()
        return None

    @staticmethod
    def _wants_open(goal: str) -> bool:
        return any(k in goal for k in ("打开", "启动", "open ", "launch"))

    @staticmethod
    def _extract_open_target(goal: str) -> Optional[str]:
        m = re.search(r"打开[「\"']?([^「\"'」]+)[」\"']?", goal)
        return m.group(1).strip() if m else None
