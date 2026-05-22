"""
Session consolidation — compress long conversations into narrative_schema (Claude-style).
"""

from __future__ import annotations

from typing import Dict, List

from core.memory.summarizer import summarize_turns
from core.memory.types import ConversationTurn


def consolidate_session(
    conversation: List[ConversationTurn],
    existing_schema: Dict,
    *,
    min_turns: int = 18,
) -> Dict | None:
    if len(conversation) < min_turns:
        return None

    summary = summarize_turns(conversation)
    if not summary:
        return None

    schema = dict(existing_schema or {})
    lt = dict(schema.get("long_term") or {})
    lt["session_summary"] = summary
    lt["turn_count_at_consolidation"] = len(conversation)
    schema["long_term"] = lt
    schema["_meta"] = {
        **(schema.get("_meta") or {}),
        "consolidated": True,
        "source": "memory_consolidator",
    }
    return schema
