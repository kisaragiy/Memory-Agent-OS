"""
Intent Router — classify every input before kernel / planner / world / memory.

Natural language MUST NOT enter execute_code unless intent is CODE with code signals.
"""

from __future__ import annotations

import ast
import re
from typing import Dict, List, Optional

from core.contracts.intent import (
    ExecutionChannel,
    IntentClassification,
    IntentRoute,
    IntentType,
)
from core.world.world_runtime import WorldRuntime

MEMORY_PREFIXES = ("remember:", "记住:", "记住：")
CODE_MARKERS = (
    "```python",
    "```py",
    "def ",
    "class ",
    "import ",
    "from ",
    "print(",
    "pip install",
    ".py",
    "python ",
    "javascript",
    "typescript",
    "sql ",
    "=>",
    "function ",
    "const ",
    "let ",
    "var ",
)
CODE_INTENT_WORDS = (
    "写代码",
    "编程",
    "代码",
    "脚本",
    "debug",
    "bug",
    "修复错误",
    "api",
    "接口",
    "函数",
    "implement",
    "refactor",
)
NARRATIVE_INTENT_WORDS = (
    "小说",
    "故事",
    "剧本",
    "恐怖",
    "续写",
    "角色",
    "剧情",
    "漫剧",
    "写一段",
    "写一篇",
    "创作",
    "大纲",
    "场景",
    "对话",
    "叙事",
    "人设",
    "世界观",
    "章节",
)
CHAT_PATTERNS = re.compile(
    r"^(你好|您好|hi|hello|hey|在吗|谢谢|感谢|ok|okay|好的|嗯|嗨)[\s!！。.?？]*$",
    re.IGNORECASE,
)


class IntentRouter:
    @classmethod
    def classify(cls, text: str, context: Optional[Dict] = None) -> IntentClassification:
        raw = (text or "").strip()
        ctx = context or {}
        reasons: List[str] = []

        for prefix in MEMORY_PREFIXES:
            if raw.lower().startswith(prefix.lower()):
                body = raw[len(prefix) :].strip()
                return IntentClassification(
                    route=IntentRoute(
                        IntentType.MEMORY,
                        ExecutionChannel.MEMORY,
                        allow_execute_code=False,
                        reasons=["memory_prefix"],
                    ),
                    normalized_task=body or raw,
                )

        if ctx.get("action_plan"):
            return IntentClassification(
                route=IntentRoute(
                    IntentType.UI,
                    ExecutionChannel.GUARD,
                    allow_execute_code=False,
                    reasons=["action_plan_present"],
                ),
                normalized_task=raw,
            )

        if CHAT_PATTERNS.match(raw):
            return IntentClassification(
                route=IntentRoute(
                    IntentType.CHAT,
                    ExecutionChannel.NARRATIVE,
                    allow_execute_code=False,
                    reasons=["chat_greeting"],
                ),
                normalized_task=raw,
            )

        if cls._has_code_signals(raw):
            reasons.append("code_signals")
            return IntentClassification(
                route=IntentRoute(
                    IntentType.CODE,
                    ExecutionChannel.PLANNER,
                    allow_execute_code=True,
                    confidence=0.9,
                    reasons=reasons,
                ),
                normalized_task=raw,
            )

        if WorldRuntime.is_narrative_task(raw, ctx) or cls._has_narrative_signals(raw):
            reasons.append("narrative_signals")
            return IntentClassification(
                route=IntentRoute(
                    IntentType.NARRATIVE,
                    ExecutionChannel.NARRATIVE,
                    allow_execute_code=False,
                    reasons=reasons,
                ),
                normalized_task=raw,
            )

        if cls.looks_like_natural_language(raw):
            reasons.append("natural_language_default_narrative")
            return IntentClassification(
                route=IntentRoute(
                    IntentType.NARRATIVE,
                    ExecutionChannel.NARRATIVE,
                    allow_execute_code=False,
                    reasons=reasons,
                ),
                normalized_task=raw,
            )

        return IntentClassification(
            route=IntentRoute(
                IntentType.UNKNOWN,
                ExecutionChannel.NARRATIVE,
                allow_execute_code=False,
                reasons=["safe_default_narrative"],
            ),
            normalized_task=raw,
        )

    @staticmethod
    def _has_code_signals(text: str) -> bool:
        lower = text.lower()
        if any(m in text for m in CODE_MARKERS):
            return True
        if any(w in lower or w in text for w in CODE_INTENT_WORDS):
            return True
        if "```" in text and ("py" in lower or "python" in lower):
            return True
        return False

    @staticmethod
    def _has_narrative_signals(text: str) -> bool:
        return any(w in text for w in NARRATIVE_INTENT_WORDS)

    @staticmethod
    def looks_like_natural_language(text: str) -> bool:
        """True when text must not be eval/exec'd as Python."""
        t = (text or "").strip()
        if not t:
            return True
        if IntentRouter._has_code_signals(t):
            return False
        if "\n" in t:
            lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
            if len(lines) > 1:
                return not any(IntentRouter._has_code_signals(ln) for ln in lines)
        try:
            tree = ast.parse(t, mode="exec")
        except SyntaxError:
            return True
        if len(tree.body) == 1 and isinstance(tree.body[0], ast.Expr):
            return True
        if len(tree.body) == 1 and isinstance(tree.body[0], ast.Pass):
            return False
        has_real_code = any(
            isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom, ast.Assign))
            for n in ast.walk(tree)
        )
        return not has_real_code

    @staticmethod
    def is_safe_python_snippet(text: str) -> bool:
        """Strict gate for passthrough execute_code — not ast.parse alone."""
        t = (text or "").strip()
        if not t or IntentRouter.looks_like_natural_language(t):
            return False
        if not IntentRouter._has_code_signals(t):
            return False
        try:
            ast.parse(t)
        except SyntaxError:
            return False
        return True
