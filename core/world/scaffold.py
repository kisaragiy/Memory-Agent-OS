"""Pure narrative scaffold from world state (no I/O, no LLM)."""

from __future__ import annotations

from core.contracts.narrative import NarrativeState
from core.contracts.world import WorldState
from core.world.dialogue_director import DialogueDirector
from core.world.narrative_engine import NarrativeEngine


def build_scaffold(
    state: WorldState,
    narrative: NarrativeState,
    world_frame: dict,
    user_prompt: str,
) -> str:
    engine = NarrativeEngine()
    passage = engine.render_passage(
        narrative.to_dict(),
        world_frame.get("characters") or {},
        world_frame.get("emotions") or {},
    )
    from core.world.character_graph import CharacterGraph

    graph = CharacterGraph()
    for name, data in (world_frame.get("characters") or {}).items():
        graph.upsert(name, data.get("role", "character"), data.get("traits"))
    director = DialogueDirector(graph)

    beats = director.plan_dialogue(state.scene or "默认场景", list(graph.nodes.keys())[:3])
    dialogue = "\n".join(
        director.render_beat(b, world_frame.get("emotions") or {})
        for b in beats.get("beats", [])
    )
    parts = [passage]
    if dialogue:
        parts.append(dialogue)
    parts.append(f"\n【续写方向】{user_prompt}")
    return "\n".join(parts)
