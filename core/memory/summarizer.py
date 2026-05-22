from __future__ import annotations

from typing import List

from core.control.model_policy import ModelPolicy
from core.llm.client import invoke_llm
from core.memory.types import ConversationTurn


def summarize_turns(turns: List[ConversationTurn], max_chars: int = 400) -> str:
    if not turns:
        return ""
    lines = [f"{t.role}: {t.content}" for t in turns[-12:]]
    blob = "\n".join(lines)
    if len(blob) <= max_chars:
        return blob
    try:
        spec = ModelPolicy.build_summarizer_invocation(blob)
        return invoke_llm(spec).strip()
    except Exception:
        return blob[:max_chars] + "…"
