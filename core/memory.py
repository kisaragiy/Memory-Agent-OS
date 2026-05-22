"""
DEPRECATED — use core.memory.memory_layer only.

Shim for legacy callers; all paths delegate to unified MemoryLayer.
"""

from core.memory import get_memory_layer


def build_prompt(user_input: str, agent_id: str = "local-agent") -> str:
    layer = get_memory_layer()
    ctx = layer.build_context(agent_id, user_input)
    return layer.format_prompt_block(ctx)


def update_memory(user: str, ai: str, agent_id: str = "local-agent"):
    from core.memory.types import ConversationTurn

    layer = get_memory_layer()
    layer._store.append_conversation(agent_id, ConversationTurn("user", user))
    layer._store.append_conversation(agent_id, ConversationTurn("assistant", ai))


def retrieve(query: str, agent_id: str = "local-agent", top_k: int = 3) -> str:
    layer = get_memory_layer()
    ctx = layer.build_context(agent_id, query)
    items = ctx.get("retrieved_memories") or []
    return "\n".join(m["content"] for m in items[:top_k])


# Legacy module-level state — no longer used; kept for import compatibility.
short_term = []
long_term = []
turn_count = 0
