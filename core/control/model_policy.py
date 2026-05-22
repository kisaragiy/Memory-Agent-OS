"""
Model Policy — sole strategy layer for LLM routing, capability shaping, safety bounds.

Model ≠ intelligence. Policy = intelligence boundary.
Forbidden: prompt/mode logic in execution_engine, memory_layer, or llm client.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from core.config.ollama_models import MODELS, TIMEOUTS
from core.contracts.intent import ExecutionChannel, IntentRoute, IntentType
from core.control.alignment_spec import AlignmentFlags, AlignmentSpec
from core.control.runtime_control import RuntimeControl


class ModelMode(str, Enum):
    USER = "user"
    DEVELOPER = "developer"
    CREATIVE = "creative"
    STRICT = "strict"


# Capability + safety envelope per mode
MODE_POLICIES: Dict[ModelMode, Dict[str, Any]] = {
    ModelMode.USER: {
        "max_tokens": 500,
        "temperature": 0.7,
        "allow_reasoning": False,
        "allow_trace": False,
        "allow_narrative": True,
        "output_style": "clean",
        "show_chain_of_thought": False,
    },
    ModelMode.DEVELOPER: {
        "max_tokens": 3000,
        "temperature": 0.6,
        "allow_reasoning": True,
        "allow_trace": True,
        "allow_narrative": True,
        "output_style": "verbose",
        "show_chain_of_thought": True,
    },
    ModelMode.CREATIVE: {
        "max_tokens": 8000,
        "temperature": 1.0,
        "allow_reasoning": False,
        "allow_trace": False,
        "allow_narrative": True,
        "output_style": "literary",
        "show_chain_of_thought": False,
    },
    ModelMode.STRICT: {
        "max_tokens": 2000,
        "temperature": 0.2,
        "allow_reasoning": False,
        "allow_trace": True,
        "allow_narrative": False,
        "output_style": "schema",
        "show_chain_of_thought": False,
    },
}

ROLE_MODEL: Dict[str, Dict[ModelMode, str]] = {
    "writer": {
        ModelMode.USER: MODELS["writer"],
        ModelMode.DEVELOPER: MODELS["writer"],
        ModelMode.CREATIVE: MODELS["writer"],
        ModelMode.STRICT: MODELS["general"],
    },
    "planner": {
        ModelMode.USER: MODELS["planner"],
        ModelMode.DEVELOPER: MODELS["planner"],
        ModelMode.CREATIVE: MODELS["planner"],
        ModelMode.STRICT: MODELS["coder"],
    },
    "coder": {
        ModelMode.STRICT: MODELS["coder"],
        ModelMode.DEVELOPER: MODELS["coder"],
    },
    "summarizer": {
        ModelMode.USER: MODELS["planner"],
        ModelMode.DEVELOPER: MODELS["planner"],
    },
    "vision": {
        ModelMode.USER: MODELS["vision"],
        ModelMode.DEVELOPER: MODELS["vision"],
    },
}

MODE_PRESETS: Dict[str, AlignmentFlags] = {
    RuntimeControl.USER: AlignmentFlags(
        show_reasoning=False,
        show_trace=False,
        show_memory=False,
        show_tool_io=False,
        show_system_meta=False,
        enable_code_execution=True,
        enable_llm_reasoning=False,
        enable_narrative=True,
        enable_vision=False,
        enable_memory_write=True,
        enable_autonomy=False,
    ),
    RuntimeControl.DEVELOPER: AlignmentFlags(
        show_reasoning=True,
        show_trace=True,
        show_memory=True,
        show_tool_io=True,
        show_system_meta=True,
        enable_code_execution=True,
        enable_llm_reasoning=True,
        enable_narrative=True,
        enable_vision=True,
        enable_memory_write=True,
        enable_autonomy=False,
    ),
    RuntimeControl.DEBUG: AlignmentFlags(
        show_reasoning=True,
        show_trace=True,
        show_memory=True,
        show_tool_io=True,
        show_system_meta=True,
        enable_code_execution=True,
        enable_llm_reasoning=True,
        enable_narrative=True,
        enable_vision=True,
        enable_memory_write=True,
        enable_autonomy=True,
    ),
}

ROLE_TIMEOUT: Dict[str, int] = {
    "writer": TIMEOUTS["writer"],
    "planner": TIMEOUTS["planner"],
    "coder": TIMEOUTS["coder"],
    "summarizer": 45,
    "vision": TIMEOUTS["vision"],
}


@dataclass
class LLMInvocationSpec:
    """Transport-only spec for core.llm.client — no policy inside client."""

    model: str
    system: str
    user: str
    max_tokens: int
    temperature: float
    timeout: int
    strip_fences: bool = False
    model_mode: str = ModelMode.USER.value
    role: str = "writer"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "timeout": self.timeout,
            "model_mode": self.model_mode,
            "role": self.role,
        }


class ModelPolicy:
    @classmethod
    def resolve_flags(cls, mode: str) -> AlignmentFlags:
        """Batch alignment preset for control mode (user / developer / debug)."""
        key = mode if mode in MODE_PRESETS else RuntimeControl.USER
        return MODE_PRESETS[key]

    @classmethod
    def resolve_alignment(cls, mode: str) -> AlignmentSpec:
        return AlignmentSpec(control_mode=mode, flags=cls.resolve_flags(mode))

    @classmethod
    def resolve_mode(
        cls,
        control_mode: str,
        intent: IntentType,
        *,
        task_type: str = "",
    ) -> ModelMode:
        if task_type in ("direct_code", "code_generation", "api_design", "debugging"):
            return ModelMode.STRICT
        if control_mode == RuntimeControl.DEBUG:
            return ModelMode.DEVELOPER
        if control_mode == RuntimeControl.DEVELOPER:
            if intent in (IntentType.NARRATIVE, IntentType.CHAT):
                return ModelMode.CREATIVE
            return ModelMode.DEVELOPER
        if intent in (IntentType.NARRATIVE, IntentType.CHAT):
            return ModelMode.CREATIVE if len(task_type) == 0 else ModelMode.USER
        if intent == IntentType.CODE:
            return ModelMode.STRICT
        return ModelMode.USER

    @classmethod
    def get_policy(cls, mode: ModelMode) -> Dict[str, Any]:
        return dict(MODE_POLICIES[mode])

    @classmethod
    def select_model(cls, mode: ModelMode, role: str) -> str:
        role_map = ROLE_MODEL.get(role, {})
        if mode in role_map:
            return role_map[mode]
        if role == "coder":
            return MODELS["coder"]
        return MODELS.get("general", MODELS["writer"])

    @classmethod
    def route_target(cls, route: IntentRoute) -> str:
        """Intent routing table (orchestrator decision)."""
        if route.channel == ExecutionChannel.MEMORY:
            return "memory"
        if route.channel == ExecutionChannel.GUARD:
            return "guard"
        if route.allow_execute_code or route.intent == IntentType.CODE:
            return "execute_code"
        return "llm"

    @classmethod
    def build_system_prompt(
        cls,
        mode: ModelMode,
        role: str,
        flags: Optional[AlignmentFlags] = None,
    ) -> str:
        policy = cls.get_policy(mode)
        flags = flags or cls.resolve_flags(RuntimeControl.USER)
        style = policy.get("output_style", "clean")
        parts = [
            "你是 Agent OS 内核调度的模型执行单元，不是独立 chatbot。",
            f"输出风格: {style}。",
        ]
        if not flags.enable_llm_reasoning or not policy.get("allow_reasoning"):
            parts.append("禁止输出推理过程、禁止  标签、禁止逐步分析。")
        if not policy.get("show_chain_of_thought"):
            parts.append("直接给出最终结果。")
        if role == "planner" or mode == ModelMode.STRICT:
            parts.append("仅输出可执行 Python 代码，无 markdown，无解释。")
        if role == "writer" and flags.enable_narrative and policy.get("allow_narrative"):
            parts.append("根据记忆与世界设定续写，保持角色一致性。")
        parts.extend(cls._safety_constraints())
        return "\n".join(parts)

    @classmethod
    def _safety_constraints(cls) -> List[str]:
        return [
            "安全边界: 不执行或编造系统命令结果；不声称已操作用户计算机。",
            "安全边界: 自然语言不得当作 Python 执行。",
            "安全边界: 用户模式下不暴露内部 trace、syscall、工具名。",
        ]

    @classmethod
    def _mode_constraints(cls, mode: ModelMode) -> str:
        p = cls.get_policy(mode)
        lines = [f"max_tokens≈{p['max_tokens']}", f"style={p['output_style']}"]
        if not p.get("allow_trace"):
            lines.append("不可提及执行链/工具调用细节。")
        return "模式约束: " + "; ".join(lines)

    @classmethod
    def build_planner_invocation(
        cls,
        context: Dict[str, Any],
        model_mode: Optional[ModelMode] = None,
    ) -> LLMInvocationSpec:
        control_mode = context.get("control_mode", RuntimeControl.USER)
        raw_flags = context.get("alignment_flags")
        flags = (
            AlignmentFlags.from_dict(raw_flags)
            if raw_flags
            else cls.resolve_flags(control_mode)
        )
        mode = model_mode or cls.resolve_mode(
            control_mode,
            IntentType.CODE,
            task_type=context.get("task_type", "code"),
        )
        policy = cls.get_policy(mode)
        memory_block = (context.get("memory_prompt") or "")[:2000]
        user_input = context.get("input", "")
        system = cls.build_system_prompt(mode, "planner", flags)
        user = f"""{cls._mode_constraints(mode)}

{memory_block}

任务:
{user_input}
"""
        return LLMInvocationSpec(
            model=cls.select_model(mode, "planner" if mode != ModelMode.STRICT else "coder"),
            system=system,
            user=user.strip(),
            max_tokens=policy["max_tokens"],
            temperature=policy["temperature"],
            timeout=ROLE_TIMEOUT["planner"],
            strip_fences=True,
            model_mode=mode.value,
            role="planner",
        )

    @classmethod
    def build_narrative_invocation(
        cls,
        render_bundle: Dict[str, Any],
        model_mode: Optional[ModelMode] = None,
    ) -> LLMInvocationSpec:
        control_mode = render_bundle.get("control_mode", RuntimeControl.USER)
        raw_flags = render_bundle.get("alignment_flags")
        flags = (
            AlignmentFlags.from_dict(raw_flags)
            if raw_flags
            else cls.resolve_flags(control_mode)
        )
        if not flags.enable_narrative:
            raise ValueError("narrative_disabled_by_alignment")

        intent_str = render_bundle.get("intent", IntentType.NARRATIVE.value)
        try:
            intent = IntentType(intent_str)
        except ValueError:
            intent = IntentType.NARRATIVE

        if model_mode is not None:
            mode = model_mode
        elif render_bundle.get("model_mode"):
            mode = ModelMode(str(render_bundle["model_mode"]))
        else:
            mode = cls.resolve_mode(control_mode, intent)

        policy = cls.get_policy(mode)
        user_prompt = render_bundle.get("prompt", "")
        scaffold = render_bundle.get("scaffold", "")
        memory_prompt = (render_bundle.get("memory_prompt") or "")[:1500]
        schema = render_bundle.get("narrative_schema") or {}
        lt = schema.get("long_term") or schema
        prefs = lt.get("user_preferences") or {} if isinstance(lt, dict) else {}

        user_body = cls._narrative_user_body(
            user_prompt, scaffold, memory_prompt, lt, prefs, mode, control_mode
        )
        system = cls.build_system_prompt(mode, "writer", flags)

        max_tokens = policy["max_tokens"]
        if control_mode == RuntimeControl.USER:
            user_policy = cls.get_policy(ModelMode.USER)
            max_tokens = min(max_tokens, int(user_policy["max_tokens"]), 800)
        elif mode == ModelMode.USER:
            max_tokens = min(max_tokens, 800)

        return LLMInvocationSpec(
            model=cls.select_model(mode, "writer"),
            system=system,
            user=f"{cls._mode_constraints(mode)}\n\n{user_body}",
            max_tokens=max_tokens,
            temperature=policy["temperature"],
            timeout=ROLE_TIMEOUT["writer"],
            strip_fences=False,
            model_mode=mode.value,
            role="writer",
        )

    @classmethod
    def _narrative_user_body(
        cls,
        user_prompt: str,
        scaffold: str,
        memory_block: str,
        lt: Dict,
        prefs: Dict,
        mode: ModelMode,
        control_mode: str = RuntimeControl.USER,
    ) -> str:
        characters = lt.get("characters") or []
        world_settings = lt.get("world_settings") or []
        world_lines = "\n".join(
            f"- {w.get('key', '设定')}: {str(w.get('value', ''))[:200]}"
            for w in world_settings[:5]
        )
        char_lines = cls._format_characters(characters)
        forbidden = prefs.get("forbidden") or []
        forb = (
            "；".join(str(x)[:80] for x in forbidden[:6])
            if isinstance(forbidden, list)
            else str(forbidden)[:200]
        ) or "无"

        length_hint = (
            "300–800 字"
            if mode == ModelMode.USER or control_mode == RuntimeControl.USER
            else "500–2000 字"
        )

        return f"""【写作风格】{str(prefs.get('writing_style', '沉浸叙事'))[:150]}
【基调】{str(prefs.get('tone', '自然'))}
【禁忌】{forb}

【世界观】
{world_lines or '（沿用上下文）'}

【角色】
{char_lines}

【世界状态摘要】
{scaffold[:800]}

【记忆上下文】
{memory_block or '无'}

【用户要求】
{user_prompt}

要求：直接输出正文，不要解释；{length_hint}。
"""

    @classmethod
    def build_summarizer_invocation(cls, conversation_blob: str) -> LLMInvocationSpec:
        mode = ModelMode.USER
        policy = cls.get_policy(mode)
        system = "你是会话摘要器。用不超过120字总结对话要点，保留人名与关键事实。"
        return LLMInvocationSpec(
            model=cls.select_model(mode, "summarizer"),
            system=system,
            user=conversation_blob[-3000:],
            max_tokens=200,
            temperature=0.3,
            timeout=ROLE_TIMEOUT["summarizer"],
            model_mode=mode.value,
            role="summarizer",
        )

    @classmethod
    def build_vision_invocation(cls, hint: str) -> LLMInvocationSpec:
        mode = ModelMode.STRICT
        policy = cls.get_policy(mode)
        system = "你是 UI 解析器。仅输出 JSON，描述可交互元素。"
        user = f"""分析这张屏幕截图，列出可交互 UI 元素。
用户意图: {hint[:500]}
输出 JSON: {{"elements": [{{"role":"button|input|link","label":"...","bbox_hint":"..."}}]}}
"""
        return LLMInvocationSpec(
            model=MODELS["vision"],
            system=system,
            user=user,
            max_tokens=min(1500, policy["max_tokens"]),
            temperature=0.1,
            timeout=ROLE_TIMEOUT["vision"],
            model_mode=mode.value,
            role="vision",
        )

    @staticmethod
    def _format_characters(characters: List[Dict]) -> str:
        if not characters:
            return "（尚未设定角色）"
        lines = []
        for c in characters[:6]:
            name = c.get("name") or "未命名"
            role = c.get("role", "角色")
            personality = (c.get("personality") or "")[:120]
            lines.append(f"- {name}（{role}）{personality}")
        return "\n".join(lines)
